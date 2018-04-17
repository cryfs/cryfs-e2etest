from cryfs.e2etest.test_framework.logger import Logger, LogLevel


def test_logger() -> None:
    logger = Logger()
    logger.log(LogLevel.INFO, "Message 1")
    logger.log(LogLevel.ERROR, "Message 2")
    assert logger.to_string() == "[INFO] Message 1\n[ERROR] Message 2\n"
