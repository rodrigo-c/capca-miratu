from apps.utils.rut import is_valid_rut


class TestIsValidRut:
    def test_wrong_format(self):
        assert is_valid_rut(rut="11.a23") is False

    def test_dv_valid(self):
        assert is_valid_rut(rut="10.000.000-8") is True

    def test_dv_invalid(self):
        assert is_valid_rut(rut="10.000.000-7") is False
