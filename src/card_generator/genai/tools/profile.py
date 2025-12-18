import asyncio
import logging
from typing import Optional

from google.genai import Client
from PIL.Image import Image

from card_generator.genai.google import (
    DEFAULT_TEXT_MODEL_NAME,
    GeminiModel,
    generate_text_response,
)
from card_generator.genai.tools.profile_cfg import PROMPT
from card_generator.image.profile import ProfilePicture

LOGGER = logging.getLogger(__name__)

_DEFAULT_PROFILE_MODEL = GeminiModel(name=DEFAULT_TEXT_MODEL_NAME)


async def enhance_profile_description(
    image: Image,
    description: Optional[str] = None,
    model: GeminiModel = _DEFAULT_PROFILE_MODEL,
    client: Optional[Client] = None,
) -> str:
    LOGGER.info('Generating profile description...')
    LOGGER.debug(f'Input profile description: {description}')
    prompt = PROMPT.format(description=description or 'N/A')
    description = await generate_text_response(
        prompt=prompt, image_content=[image], model=model, client=client
    )

    LOGGER.debug(f'Generated profile description: {description}')
    return description


async def enhance_profile_descriptions(
    profiles: list[ProfilePicture],
    model: GeminiModel = _DEFAULT_PROFILE_MODEL,
    client: Optional[Client] = None,
) -> list[ProfilePicture]:
    coroutines = [
        enhance_profile_description(
            image=profile.image,
            description=profile.description,
            model=model,
            client=client,
        )
        for profile in profiles
    ]
    expanded_descriptions = await asyncio.gather(*coroutines)
    enhanced_profiles = [
        ProfilePicture(image=profile.image, description=description)
        for profile, description in zip(profiles, expanded_descriptions)
    ]
    return enhanced_profiles
