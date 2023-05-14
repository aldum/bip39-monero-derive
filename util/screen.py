
def yesno_to_bool(yn: str) -> bool:
    ci = yn.lower()
    return ci in ('yes', 'y')


def bool_to_yesno(b: bool) -> str:
    if b:
        return 'yes'
    return 'no'
