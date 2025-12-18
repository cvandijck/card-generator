import logging
from typing import Optional

from google.genai import Client
from PIL.Image import Image

from card_generator.genai.google import (
    DEFAULT_IMAGE_MODEL_NAME,
    GeminiModel,
    generate_image_response,
)
from card_generator.genai.tools.card_cfg import PROMPT
from card_generator.image.profile import ProfilePicture

LOGGER = logging.getLogger(__name__)

_DEFAULT_MODEL = GeminiModel(name=DEFAULT_IMAGE_MODEL_NAME)


async def generate_card(
    family_members: list[ProfilePicture],
    scene_instructions: str,
    overlay_instructions: str = 'N/A',
    style_instructions: str = 'N/A',
    model: GeminiModel = _DEFAULT_MODEL,
    client: Optional[Client] = None,
) -> Image:
    LOGGER.info('Generating card image...')

    family_member_descriptions = '\n'.join([f'- {str(pic)}' for pic in family_members])

    prompt = PROMPT.format(
        family_members_descriptions=family_member_descriptions,
        scene_instructions=scene_instructions,
        overlay_instructions=overlay_instructions,
        style_instructions=style_instructions,
    )

    family_members_images = [pic.image for pic in family_members]

    return await generate_image_response(
        prompt=prompt,
        image_content=family_members_images,
        model=model,
        aspect_ratio='4:3',
        add_grounding=True,
        client=client,
    )
