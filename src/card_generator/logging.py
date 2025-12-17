import logging
import sys
from pathlib import Path
from typing import Literal, Optional

DEFAULT_LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class PackageFilter(logging.Filter):
    def __init__(self, package_name):
        super().__init__()
        self.package_name = package_name

    def filter(self, record):
        return record.name.startswith(self.package_name)


def configure_logging(
    level=logging.INFO,
    log_format: str = DEFAULT_LOGGING_FORMAT,
    log_file_path: Optional[Path] = None,
    log_file_mode: Literal['w', 'a'] = 'a',
    exclude_external_logs: bool = False,
):
    logger = logging.getLogger()
    logger.setLevel(logging.NOTSET)  # Let the handlers decide the level

    formatter = logging.Formatter(log_format)

    if log_file_path:
        file_handler = logging.FileHandler(filename=str(log_file_path), mode=log_file_mode)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)

    if exclude_external_logs:
        package_name = __name__.split('.')[0]
        package_filter = PackageFilter(package_name)
        logger.addFilter(package_filter)


def convert_logging_level(level: str) -> int:
    # in python 3.11 logging.getLevelName is deprecated

    if sys.version_info < (3, 11):
        return logging.getLevelName(level)

    mapping = logging.getLevelNamesMapping()

    if level.upper() not in mapping:
        raise ValueError(f'Invalid log level: {level}')

    return mapping[level.upper()]
