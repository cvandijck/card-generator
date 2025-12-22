import logging
from typing import Optional

from google.genai import Client
from PIL.Image import Image

from card_generator.genai.google import (
    DEFAULT_IMAGE_MODEL_NAME,
    AspectRatio,
    GeminiModel,
    Resolution,
    generate_image_response,
)
from card_generator.genai.tools.card_cfg import PROMPT
from card_generator.image.profile import Profile

LOGGER = logging.getLogger(__name__)

_DEFAULT_MODEL = GeminiModel(name=DEFAULT_IMAGE_MODEL_NAME)


async def generate_card(
    profiles: list[Profile],
    scene_instructions: str,
    overlay_instructions: str = 'N/A',
    style_instructions: str = 'N/A',
    aspect_ratio: AspectRatio = '4:3',
    resolution: Resolution = '1K',
    model: GeminiModel = _DEFAULT_MODEL,
    client: Optional[Client] = None,
) -> Image:
    LOGGER.info('Generating card image...')

    profile_descriptions = str(profiles)

    prompt = PROMPT.format(
        profile_descriptions=profile_descriptions,
        scene_instructions=scene_instructions,
        overlay_instructions=overlay_instructions,
        style_instructions=style_instructions,
    )

    profile_images = [profile.image for profile in profiles]

    return await generate_image_response(
        prompt=prompt,
        image_content=profile_images,
        model=model,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        add_grounding=True,
        client=client,
    )
