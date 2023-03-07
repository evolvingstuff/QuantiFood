from conversion.utils import to_float
from conversion.constants import PRODUCES, KEYWORD_OF
from conversion.line_item import LineItem


class ProductionRule:
    def __init__(self, rule: str):
        assert PRODUCES in rule, 'Invalid rule'
        self.lhs, self.rhs = [part.strip() for part in rule.split(PRODUCES)]

        # parse LHS
        parts = [s.strip() for s in self.lhs.split()]
        if KEYWORD_OF in parts:
            of_index = parts.index(KEYWORD_OF)
            if of_index == 1:
                # unit of thing1[ thing2]
                self.lhs_line_item = LineItem(None, parts[0], ' '.join(parts[2:]))
            elif of_index == 2:
                if to_float(parts[0]) is not None:
                    # number unit of thing1[ thing2]
                    self.lhs_line_item = LineItem(to_float(parts[0]), parts[1], ' '.join(parts[3:]))
                else:
                    print(f'DEBUG: {parts[0]}')
                    raise Exception('Illegal parse of LHS')
            else:
                raise Exception('Illegal parse of LHS')
        else:
            if to_float(parts[0]) is not None:
                # number thing1[ thing2]
                self.lhs_line_item = LineItem(to_float(parts[0]), None, ' '.join(parts[1:]))
            else:
                # thing1[ thing2]
                self.lhs_line_item = LineItem(1, None, ' '.join(parts))

        # parse RHS
        self.rhs_line_items = []
        for e, entry in enumerate([p.strip() for p in self.rhs.split(',')]):
            # parse entry
            parts = [s.strip() for s in entry.split()]
            if KEYWORD_OF in parts:
                of_index = parts.index(KEYWORD_OF)
                if of_index == 2:
                    if to_float(parts[0]) is not None:
                        # number unit of thing1[ thing2]
                        self.rhs_line_items.append(LineItem(to_float(parts[0]), parts[1], ' '.join(parts[3:])))
                    else:
                        raise Exception('Illegal parse of LHS')
                else:
                    raise Exception('Illegal parse of LHS')
            else:
                if to_float(parts[0]) is not None:
                    # number thing1[ thing2]
                    self.rhs_line_items.append(LineItem(to_float(parts[0]), None, ' '.join(parts[1:])))
                else:
                    # thing1[ thing2]
                    self.rhs_line_item = LineItem(1, None, ' '.join(parts))

    def __str__(self):
        return f'{str(self.lhs_line_item)} => {", ".join([str(li) for li in self.rhs_line_items])}'
