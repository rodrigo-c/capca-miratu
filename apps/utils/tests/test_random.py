from apps.utils.random import get_random_url_code


def test_get_random_url_code():
    random_code = get_random_url_code()
    assert isinstance(random_code, str)
