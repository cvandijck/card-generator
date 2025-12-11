import logging
from typing import Optional

from google.genai import Client
from PIL.Image import Image

from card_generator.genai.google import (
    GeminiModel,
    GeminiModelName,
    generate_text_response,
)

LOGGER = logging.getLogger(__name__)

_DEFAULT_PROFILE_MODEL = GeminiModel(name=GeminiModelName.GEMINI_2_5_FLASH)
_PROMPT = """
You are an agent working in a system that generates personalized greeting cards.

You are an expert at creating written profiles for individuals that will be used to generate images of them.
Your task is to create a detailed written profile for each individual based on a provided picture and (optionally) a short user-provided description.
The written profile should capture the key physical characteristics and personality traits of the individual as inferred
from the picture and description to ensure accurate representation in the final generated image.

The profile should be concise yet descriptive, focusing on aspects such as facial features, expressions, attire, and any notable attributes.
The profile should be formatted as a single paragraph of text.

<UserProvidedDescription>
{description}
</UserProvidedDescription>

Profile description:
"""


async def generate_profile_description(
    image: Image,
    description: Optional[str] = None,
    model: GeminiModel = _DEFAULT_PROFILE_MODEL,
    client: Optional[Client] = None,
) -> str:
    LOGGER.info('Generating profile description...')
    LOGGER.debug(f'Input profile description: {description}')
    prompt = _PROMPT.format(description=description or 'N/A')
    description = await generate_text_response(
        prompt=prompt, image_content=[image], model=model, client=client
    )

    LOGGER.debug(f'Generated profile description: {description}')
    return description
