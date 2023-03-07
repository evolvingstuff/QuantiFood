from conversion.constants import *
import conversion.parser as parser


def main():
    production_rules = []
    conversion_rules = []
    with open('data.txt', 'r') as f:  # TODO 2023.01.31 how to specify?
        lines = f.readlines()
        for line in lines:
            if line == '' or line.strip().startswith(COMMENT):
                continue
            parser.parse(line, production_rules, conversion_rules)
    while True:
        user_input = input('> ')
        if user_input == QUIT:
            return
        elif user_input == HELP:
            print('Type a rule in the form of: A => B, or A = B')
            print('Type ? for a summary of the rules')
            print('Type <expression>? for inference')
        elif user_input == '?':
            display_summary(production_rules, conversion_rules)
        else:
            parser.parse(user_input, production_rules, conversion_rules)


def display_summary(production_rules, conversion_rules):
    units_of_measure = []
    types_of_things = []
    for rule in production_rules:
        if rule.lhs_line_item.unit_of_measure is not None and rule.lhs_line_item.unit_of_measure not in units_of_measure:
            units_of_measure.append(rule.lhs_line_item.unit_of_measure)
        if rule.lhs_line_item.title is not None and rule.lhs_line_item.title not in types_of_things:
            types_of_things.append(rule.lhs_line_item.title)
        for rhs_line_item in rule.rhs_line_items:
            if rhs_line_item.unit_of_measure is not None and rhs_line_item.unit_of_measure not in units_of_measure:
                units_of_measure.append(rhs_line_item.unit_of_measure)
            if rhs_line_item.title is not None and rhs_line_item.title not in types_of_things:
                types_of_things.append(rhs_line_item.title)
    for rule in conversion_rules:
        if rule.lhs_line_item.unit_of_measure is not None and rule.lhs_line_item.unit_of_measure not in units_of_measure:
            units_of_measure.append(rule.lhs_line_item.unit_of_measure)
        if rule.lhs_line_item.title is not None and rule.lhs_line_item.title not in types_of_things:
            types_of_things.append(rule.lhs_line_item.title)
        if rule.rhs_line_item.unit_of_measure is not None and rule.rhs_line_item.unit_of_measure not in units_of_measure:
            units_of_measure.append(rule.rhs_line_item.unit_of_measure)
        if rule.rhs_line_item.title is not None and rule.rhs_line_item.title not in types_of_things:
            types_of_things.append(rule.rhs_line_item.title)
    if len(units_of_measure) > 0:
        print('')
        print(f'{len(units_of_measure)} Units of measure:')
        for u in sorted(units_of_measure):
            print(f'\t{u}')
    if len(types_of_things) > 0:
        print('')
        print(f'{len(types_of_things)} Types of things:')
        for t in sorted(types_of_things):
            print(f'\t{t}')
    conversions = parser.calculate_conversions(conversion_rules)
    print('')
    print('extended unit_of_measure_conversions:')
    for unit in sorted(conversions.keys()):
        print(f'\t1 {unit}: {conversions[unit]}')


if __name__ == '__main__':
    main()
