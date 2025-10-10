import logging
from src import logging_setup


# ##################################################################
# test setup logger
# verifies setup logger creates a valid logger
def test_setup_logger():
    logger = logging_setup.setup_logger("test_logger")
    assert logger is not None
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.INFO


# ##################################################################
# test get logger
# verifies get logger returns a valid logger
def test_get_logger():
    logger = logging_setup.get_logger("test_module")
    assert logger is not None
    assert isinstance(logger, logging.Logger)


# ##################################################################
# test logger has handlers
# verifies logger has file and console handlers
def test_logger_has_handlers():
    logger = logging_setup.get_logger("test_handlers")
    assert len(logger.handlers) >= 2
    handler_types = [type(h).__name__ for h in logger.handlers]
    assert "FileHandler" in handler_types
    assert "StreamHandler" in handler_types
