import logging
import sys

def set_log_handler(logger, level):
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False  # 防止重复打印
    return logger