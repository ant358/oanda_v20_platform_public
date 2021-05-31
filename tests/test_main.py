import logging
import oanda_v20_platform.main as main


def test_logging(caplog):
    main
    logger = logging.getLogger(__name__)
    with caplog.at_level(logging.WARNING):
        logger.warning("Testing logging setup has initiated correctly")
    assert 'Testing logging setup' in caplog.text
