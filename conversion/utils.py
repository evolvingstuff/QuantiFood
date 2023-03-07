def to_float(string: str) -> bool:
    try:
        if '/' in string and ' ' not in string:
            num, den = string.split('/')
            return float(num)/float(den)
        else:
            return float(string)
    except:
        return None