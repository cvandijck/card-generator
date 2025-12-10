import argparse
import logging
from pathlib import Path

from card_generator import __version__
from card_generator.resources import get_resource_path
from card_generator.exceptions import CodedError, UnknownError


LOGGER = logging.getLogger(name='card_generator')


def process(input_file: Path, output_file: Path, log_file: Path):
    """Function to call the application's functionality.

    Args:
        input_file: path to input file
        output_file: path to write output
        log_file: path to store log file

    Raises:
        UnknownError: raised when an unspecified exception was thrown by our application

    """
    LOGGER.info(f'Running card_generator {__version__}')

    try:
        # ADD YOUR CODE HERE
        ...
    except Exception as e:
        LOGGER.error(f'Unknown exception raised\n{str(e)}')
        raise UnknownError from e
    # ADD SPECIFIC EXCEPTIONS WITH ASSIGNED EXIT CODES

    LOGGER.info('Exiting successfully')


def main():
    parser = argparse.ArgumentParser(
        prog=f'card_generator {__version__}',
        description='Generate fun artificial cards for holidays or other occassions',
    )
    parser.add_argument('input_file', help='Input file to run card_generator')
    parser.add_argument('output_file', help='Output of card_generator will be written here')

    args = parser.parse_args()
    input_file = args.input_file
    output_file = args.output_file

    try:
        process(input_file, output_file)
    except CodedError as e:
        LOGGER.error(e)
        exit(e.exit_code)
    # HANDLE SPECIFIC EXCEPTIONS AND EXIT WITH THEIR EXIT CODES


if __name__ == '__main__':
    main()
