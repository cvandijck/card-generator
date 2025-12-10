import os
from pathlib import Path

from dotenv import load_dotenv
from google.genai import Client
from google.genai.types import GenerateContentConfig, ImageConfig, Part
from pydantic import BaseModel

load_dotenv()

DATA_DIR = Path(__file__).parent / 'data'


class Picture(BaseModel):
    path: Path
    person: str
    description: str


PROMPT_TEMPLATE = """
Create a fun family image to be used as a Christmas card.

You are provided with pictures of each family member. The family consists of (in the order of the provided pictures):
{family_members}

The scene to be depicted is as follows:
{scene_description}

General instructions:
- Keep the faces and appearances of each family member consistent with the provided pictures.
- Ensure the overall image has a festive and joyful atmosphere.

{overlay_instructions}
"""

SCENE = """
The family needs to be dressed in Christmas sweaters and are sliding down a snowy hill on a sled.
The sled is going very fast and there is snow flying everywhere.
While the parents are panicking, the kids are having a great time.
"""

OVERLAY_INSTRUCTIONS = """
Overlay the image with the text "Happy Holidays!" in a playful font.
"""

MODEL_NAME = 'gemini-3-pro-image-preview'


def main():
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError('GEMINI_API_KEY environment variable not set.')

    client = Client(api_key=api_key)

    # define the input
    pictures = [
        Picture(
            path=DATA_DIR / 'christophe.jpg',
            person='Christophe',
            description='Father of the family',
        ),
        Picture(
            path=DATA_DIR / 'sara.jpg',
            person='Sara',
            description='Mother of the family',
        ),
        Picture(
            path=DATA_DIR / 'lou.jpg',
            person='Lou',
            description='Oldest son, 5 years old',
        ),
        Picture(
            path=DATA_DIR / 'mil.jpg',
            person='Mil',
            description='Youngest son, 3 years old',
        ),
    ]

    family_descriptions = '\n'.join(
        [f'- {pic.person}: {pic.description}' for pic in pictures]
    )
    prompt = PROMPT_TEMPLATE.format(
        family_members=family_descriptions,
        scene_description=SCENE,
        overlay_instructions=OVERLAY_INSTRUCTIONS,
    )

    image_contents = [
        Part.from_bytes(data=pic.path.read_bytes(), mime_type='image/jpeg')
        for pic in pictures
    ]
    image_contents.append(Part.from_text(text=prompt))

    aspect_ratio = (
        '3:2'  # "1:1","2:3","3:2","3:4","4:3","4:5","5:4","9:16","16:9","21:9"
    )
    resolution = '1K'  # "1K", "2K", "4K"

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[prompt, *image_contents],
        config=GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE'],
            image_config=ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=resolution,
            ),
        ),
    )

    for part in response.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = part.as_image()
            image.save(DATA_DIR / 'generated_image.png')


if __name__ == '__main__':
    main()
