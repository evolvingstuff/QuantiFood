import conversion.parser as parser


def test_calculate_conversions():
    # empty case
    assert parser.calculate_conversions({}) == {}
