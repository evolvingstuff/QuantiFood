from conversion.constants import KEYWORD_OF


class LineItem:
    def __init__(self, amount: float, unit_of_measure: str, title: str):
        self.amount = amount
        self.unit_of_measure = unit_of_measure
        self.title = title  # TODO rename this "name"?

    def get_unit_name(self):
        if self.title is None:
            return self.unit_of_measure
        else:
            if self.unit_of_measure is None:
                return self.title
            else:
                return f'{self.unit_of_measure} {KEYWORD_OF} {self.title}'

    def get_display_version(self):
        assert self.title is not None
        assert self.amount is not None
        if self.unit_of_measure is None:
            return f'{self.title}: {self.amount:.2f}'
        else:
            return f'{self.title}: {self.amount:.2f} {self.unit_of_measure}'

    def __str__(self):
        if self.unit_of_measure is None:
            if self.amount == 1.:
                return f'1 {self.title}'
            else:
                return f'{self.amount:.2f} {self.title}'
        else:
            if self.title is None:
                return f'{self.amount}:.2f {self.unit_of_measure}'
            else:
                return f'{self.amount:.2f} {self.unit_of_measure} of {self.title}'
