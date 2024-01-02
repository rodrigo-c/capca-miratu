import re


def is_valid_rut(rut) -> bool:
    def _get_partial_sum(base) -> int:
        factors = [2, 3, 4, 5, 6, 7]
        partial_sum = 0
        factor_position = 0
        for digit in reversed(base):
            partial_sum += int(digit) * factors[factor_position]
            factor_position = (factor_position + 1) % 6
        return partial_sum

    format_regex = r"^((\d{1,3}(\.\d{3})+-)|\d+-?)(\d|k|K)$"
    if re.match(format_regex, rut) is None:
        return False
    cleaned_rut = format_rut(rut=rut)
    base, dv = cleaned_rut.split("-")
    verification_digit = (11 - _get_partial_sum(base=base) % 11) % 11
    verification_digit = str(verification_digit) if verification_digit < 10 else "K"
    return verification_digit == dv


def format_rut(rut) -> str:
    return re.sub(r"[^K^\d^-]", "", rut.upper())
