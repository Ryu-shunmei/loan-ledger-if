import sys
import logging
from pprint import pformat
from loguru import logger
from loguru._defaults import LOGURU_FORMAT
from configs import log_settings


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def format_record(record: dict) -> str:
    format_string = LOGURU_FORMAT
    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=4, compact=True, width=88
        )
        format_string += "\n<level>{extra[payload]}</level>"

    format_string += "{exception}\n"
    return format_string


async def register():
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(log_settings.LEVEL)

    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    logger.configure(
        handlers=[
            {"sink": sys.stdout},
            {
                "sink": log_settings.PATH,
                "level": log_settings.LEVEL,
                "retention": log_settings.RETENTION,
                "format": format_record,
            },
        ]
    )
