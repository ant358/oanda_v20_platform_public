from oanda_v20_platform.config import args
import argparse
import configparser
from oanda_v20_platform.utils.fileops import get_abs_path


def test_args():
    x = args.parse_args(["--bot=rsi_bot", "--pair='EUR_USD'"])
    message = "Parse args function is not reading args"
    assert isinstance(x, argparse.Namespace), message


def test_config_ini():
    config_local = configparser.ConfigParser()
    config_local.read(get_abs_path(['config', 'config.ini']))
    message = "Cant read config.ini file with config parser"
    assert config_local.getboolean('Other', 'test'), message
