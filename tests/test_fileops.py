from oanda_v20_platform.utils.fileops import get_abs_path


def test_get_abs_path():

    x = get_abs_path()
    assert x.is_file(), "Absolute path not generated correctly!"
