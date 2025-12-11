import asyncio
import logging
from pathlib import Path

from dotenv import load_dotenv

from card_generator.genai.tools.card import generate_card
from card_generator.image.profile import ProfilePicture
from card_generator.logging import configure_logging

load_dotenv()

DATA_DIR = Path(__file__).parent / 'data'
INPUT_DIR = DATA_DIR / 'input'
OUTPUT_DIR = DATA_DIR / 'output'

SCENE_INSTRUCTIONS = """
The family needs to be dressed in Christmas sweaters and are sliding down a snowy hill on a sled.
The sled is going very fast and there is snow flying everywhere.
While the parents are panicking, the kids are having a great time.

The background should feature the city of Ghent, Belgium.
"""

OVERLAY_INSTRUCTIONS = """
Overlay the image with the text "Happy Holidays!" in a playful font.
"""


async def main():
    configure_logging(level=logging.DEBUG, exclude_external_logs=True)

    # define the input
    pictures = [
        ProfilePicture.from_filepath(
            path=INPUT_DIR / 'christophe.jpg',
            person='Christophe',
            description='Father of the family',
        ),
        ProfilePicture.from_filepath(
            path=INPUT_DIR / 'sara.jpg',
            person='Sara',
            description='Mother of the family',
        ),
        ProfilePicture.from_filepath(
            path=INPUT_DIR / 'lou.jpg',
            person='Lou',
            description='Oldest son, 5 years old',
        ),
        ProfilePicture.from_filepath(
            path=INPUT_DIR / 'mil.jpg',
            person='Mil',
            description='Youngest son, 3 years old',
        ),
    ]

    image = await generate_card(
        family_members=pictures,
        topic='',
        scene_instructions=SCENE_INSTRUCTIONS,
        overlay_instructions=OVERLAY_INSTRUCTIONS,
        style_instructions='Use the cartoon style of suske and wiske comics.',
        expand_profile_descriptions=True,
    )
    image.save(OUTPUT_DIR / 'generated_image.png')


if __name__ == '__main__':
    asyncio.run(main())
