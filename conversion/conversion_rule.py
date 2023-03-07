from conversion.utils import to_float
from conversion.constants import CONVERTS, KEYWORD_OF
from conversion.line_item import LineItem


class ConversionRule:
    def __init__(self, rule: str):
        assert CONVERTS in rule, \
            'Invalid rule'
        self.lhs, self.rhs = [part.strip() for part in rule.split(CONVERTS)]
        self.lhs_is_typed = False
        self.rhs_is_typed = False

        # parse LHS
        assert ',' not in self.lhs, \
            'Cannot use multiple line items in equality rules'
        parts = [s.strip() for s in self.lhs.split()]
        if KEYWORD_OF in parts:
            assert parts.index(KEYWORD_OF) == 2
            self.lhs_is_typed = True
            self.lhs_line_item = LineItem(float(parts[0]), parts[1], " ".join(parts[3:]))
        else:
            assert len(parts) >= 2 and to_float(parts[0]) is not None, \
                'Illegal parse'
            self.lhs_line_item = LineItem(float(parts[0]), parts[1], None)

        # parse RHS
        assert ',' not in self.rhs, \
            'Cannot use multiple line items in equality rules'
        parts = [s.strip() for s in self.rhs.split()]
        if KEYWORD_OF in parts:
            assert parts.index(KEYWORD_OF) == 2
            self.rhs_is_typed = True
            self.rhs_line_item = LineItem(float(parts[0]), parts[1], " ".join(parts[3:]))
        else:
            assert len(parts) >= 2 and to_float(parts[0]) is not None, \
                'Illegal parse'
            self.rhs_line_item = LineItem(float(parts[0]), parts[1], None)

        assert self.lhs_is_typed == self.rhs_is_typed, \
            'expect that either both sides are typed conversions, or neither'
        if self.lhs_is_typed:
            assert self.lhs_line_item.title == self.rhs_line_item.title, \
                'Only allowed to do typed conversions on the same type of thing.\n' +\
                'You probably want a production rule (=>) instead.'

    def __str__(self):
        return f'{self.lhs_line_item} = {self.rhs_line_item}'
