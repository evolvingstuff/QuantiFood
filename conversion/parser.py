from conversion.utils import to_float
from conversion.constants import *
from conversion.line_item import LineItem
from conversion.production_rule import ProductionRule
from conversion.conversion_rule import ConversionRule


def calculate_conversions(conversion_rules):
    # TODO: look for circular inconsistencies and warn user
    conversions = {}
    for rule in conversion_rules:
        lhs_amount = rule.lhs_line_item.amount
        rhs_amount = rule.rhs_line_item.amount
        # TODO 2023.01.30: here is where we lose the info about the line_items themselves
        lhs_unit_name = rule.lhs_line_item.get_unit_name()
        rhs_unit_name = rule.rhs_line_item.get_unit_name()
        assert lhs_unit_name != rhs_unit_name
        if lhs_unit_name not in conversions:
            conversions[lhs_unit_name] = {}
        if rhs_unit_name not in conversions:
            conversions[rhs_unit_name] = {}
        conversions[lhs_unit_name][rhs_unit_name] = rhs_amount / lhs_amount
        conversions[rhs_unit_name][lhs_unit_name] = lhs_amount / rhs_amount
    # tidy up
    # del rule, lhs_amount, rhs_amount, lhs_unit_name, rhs_unit_name

    # propagate extensions
    changed = True
    while changed:
        changed = False
        unit1_name_keys = sorted(list(conversions.keys()))[:]
        for unit1_name in unit1_name_keys:
            unit2_name_keys = list(conversions[unit1_name].keys())[:]
            for unit2_name in unit2_name_keys:
                if unit1_name == unit2_name:
                    continue
                unit3_name_keys = list(conversions[unit2_name].keys())[:]
                for unit3_name in unit3_name_keys:
                    if unit3_name == unit1_name:
                        continue
                    if unit3_name not in unit2_name_keys:
                        conversion_rate = conversions[unit1_name][unit2_name] * \
                                          conversions[unit2_name][unit3_name]
                        conversions[unit1_name][unit3_name] = conversion_rate
                        changed = True
    # del changed, unit1_name, unit1_name_keys, unit2_name, unit2_name_keys, unit3_name, unit3_name_keys

    # propagate extensions, part 2
    # this is a bit hacky, but feels easier than carrying around more data types
    updated = True
    while updated is True:
        updated = False
        updates = {}
        unit1_name_keys = sorted(list(conversions.keys()))[:]
        for unit1_name in unit1_name_keys:
            if f' {KEYWORD_OF} ' not in unit1_name:
                continue
            parts = [x.strip() for x in unit1_name.split(KEYWORD_OF)]
            unit1, thing1 = parts[0], " ".join(parts[1:])
            del parts
            if unit1 not in conversions.keys():
                for unit2_name in conversions[unit1_name].keys():
                    parts2 = [x.strip() for x in unit2_name.split(KEYWORD_OF)]
                    unit2, thing2 = parts2[0], " ".join(parts2[1:])
                    assert thing1 == thing2
                    if unit2 in conversions.keys():
                        assert KEYWORD_OF not in unit2
                        for unit3 in conversions[unit2]:
                            assert KEYWORD_OF not in unit3
                            new_unit_name = f'{unit3} {KEYWORD_OF} {thing1}'
                            new_unit_amount = conversions[unit2][unit3] * conversions[unit1_name][unit2_name]
                            reverse_new_unit_amount = 1. / new_unit_amount
                            if new_unit_name not in conversions[unit1_name].keys():
                                # add forward direction
                                if unit1_name not in updates:
                                    updates[unit1_name] = {}
                                updates[unit1_name][new_unit_name] = new_unit_amount
                                updated = True
                            if new_unit_name not in conversions.keys():
                                # add reverse
                                if new_unit_name not in updates:
                                    updates[new_unit_name] = {}
                                updates[new_unit_name][unit1_name] = reverse_new_unit_amount
                                updated = True
            else:
                for unit2 in conversions[unit1].keys():
                    assert unit1 != unit2
                    new_unit_name = f'{unit2} {KEYWORD_OF} {thing1}'
                    new_unit_amount = conversions[unit1][unit2]
                    reverse_new_unit_amount = 1. / new_unit_amount
                    if new_unit_name not in conversions[unit1_name]:
                        if unit1_name not in updates:
                            updates[unit1_name] = {}
                        updates[unit1_name][new_unit_name] = new_unit_amount
                        updated = True
                    if new_unit_name not in conversions or unit1_name not in conversions[new_unit_name]:
                        if new_unit_name not in updates:
                            updates[new_unit_name] = {}
                        updates[new_unit_name][unit1_name] = reverse_new_unit_amount
                        updated = True
        for key in updates:
            if key not in conversions:
                conversions[key] = updates[key]
            else:
                for key2 in updates[key]:
                    if key2 not in conversions[key]:
                        conversions[key][key2] = updates[key][key2]
    return conversions


def attempt_run_query(query, production_rules, conversion_rules):
    if f' {KEYWORD_IN} ' in query:
        filter, query = [x.strip() for x in query.split(f' {KEYWORD_IN} ')]
        filters = [x.strip() for x in filter.split(',') if x.strip() != '']
    else:
        query = query.strip()
        filters = None
    # parse query
    query_line_items = []
    for entry in [s.strip() for s in query.split(',')]:
        parts = [s.strip() for s in entry.split()]
        if KEYWORD_OF in parts:
            # number unit of thing1[ thing2]
            of_index = parts.index(KEYWORD_OF)
            assert of_index == 2, 'Illegal parse'
            if to_float(parts[0]) is not None:
                # number unit of thing1[ thing2]
                query_line_items.append(LineItem(to_float(parts[0]), parts[1], ' '.join(parts[3:])))
            else:
                raise Exception('Illegal parse of LHS')
        else:
            if to_float(parts[0]) is not None:
                # number thing1[ thing2]
                query_line_items.append(LineItem(to_float(parts[0]), None, ' '.join(parts[1:])))
            else:
                # thing1[ thing2]
                query_line_items.append(LineItem(1, None, ' '.join(parts)))
    conversions = calculate_conversions(conversion_rules)
    matches = []
    for query in query_line_items:
        matches.extend(resolve_query(query, production_rules, conversions))
    inferred_matches = matches[:]
    while True:
        all_new_matches = []
        for query in inferred_matches:
            new_matches = resolve_query(query, production_rules, conversions)
            all_new_matches.extend(new_matches)
        if len(all_new_matches) == 0:
            break
        matches.extend(all_new_matches)
        inferred_matches = all_new_matches[:]
    consolidated_matches = consolidate_matches(matches, conversions)
    matched_one_or_more = False
    for match in sorted(consolidated_matches, key=lambda x: x.get_display_version()):
        if filters is None:
            print(f'\t{match.get_display_version()}')
            matched_one_or_more = True
        elif match.title in filters:
            print(f'\t{match.get_display_version()}')
            matched_one_or_more = True
    if not matched_one_or_more:
        print('\t(no matches)')


def consolidate_matches(matches, conversions):
    # combine items with exact matches for units of measure
    for i in range(len(matches)):
        if matches[i] is None:
            continue
        for j in range(i+1, len(matches)):
            if matches[j] is None:
                continue
            if matches[i].title == matches[j].title and matches[i].unit_of_measure == matches[j].unit_of_measure:
                matches[i].amount += matches[j].amount
                matches[j] = None
    consolidated = [m for m in matches if m is not None]

    # combine items with non-exact matches for units of measure
    for i in range(len(consolidated)):
        for j in range(i + 1, len(consolidated)):
            if consolidated[i].title == consolidated[j].title:
                try:
                    assert consolidated[i].unit_of_measure != consolidated[j].unit_of_measure
                    multiplier_j_to_i = conversions[consolidated[j].get_unit_name()][consolidated[i].get_unit_name()]
                    added_to_i = consolidated[j].amount * multiplier_j_to_i
                    multiplier_i_to_j = conversions[consolidated[i].get_unit_name()][consolidated[j].get_unit_name()]
                    added_to_j = consolidated[i].amount * multiplier_i_to_j
                    consolidated[i].amount += added_to_i
                    consolidated[j].amount += added_to_j
                except Exception as e:
                    print(f'ERROR: {e}')
                    print(f'This may indicate there is a missing conversion between {consolidated[i].get_unit_name()} and {consolidated[j].get_unit_name()}')
    return consolidated


def resolve_query(query, production_rules, conversions):
    matches = []
    for pr in production_rules:
        if pr.lhs_line_item.title is None or query.title != pr.lhs_line_item.title:
            continue
        if pr.lhs_line_item.unit_of_measure is None:
            assert query.unit_of_measure is None, 'expected query not to have unit of measure either'
            multiplier = query.amount / pr.lhs_line_item.amount
        else:
            # TODO 2023.01.29: may need to handle some other edge cases here...
            if query.get_unit_name() in conversions:
                if query.get_unit_name() == pr.lhs_line_item.get_unit_name():
                    multiplier = 1.
                else:
                    # TODO 2023.01.31: if key error here, give warning about a missing conversion
                    multiplier = conversions[query.get_unit_name()][pr.lhs_line_item.get_unit_name()]
            else:
                if query.unit_of_measure == pr.lhs_line_item.unit_of_measure:
                    multiplier = 1.
                else:
                    # TODO 2023.01.31: if key error here, give warning about a missing conversion
                    multiplier = conversions[query.unit_of_measure][pr.lhs_line_item.unit_of_measure]
            multiplier *= query.amount / pr.lhs_line_item.amount
        for rhs_line_item in pr.rhs_line_items:
            matches.append(LineItem(rhs_line_item.amount * multiplier, rhs_line_item.unit_of_measure, rhs_line_item.title))
    return matches


def parse(user_input, production_rules, conversion_rules):
    if user_input == HELP:
        print('Type a rule in the form of: A => B, or A = B')
    elif PRODUCES in user_input:
        production_rules.append(ProductionRule(user_input))
    elif CONVERTS in user_input:
        conversion_rules.append(ConversionRule(user_input))
    else:
        attempt_run_query(user_input, production_rules, conversion_rules)