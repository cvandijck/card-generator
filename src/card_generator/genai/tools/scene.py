import logging
from typing import Optional

from google.genai import Client

from card_generator.genai.google import (
    DEFAULT_TEXT_MODEL_NAME,
    GeminiModel,
    generate_text_response,
)
from card_generator.genai.tools.scene_cfg import PROMPT

LOGGER = logging.getLogger(__name__)

_DEFAULT_SCENE_MODEL = GeminiModel(name=DEFAULT_TEXT_MODEL_NAME)


async def enhance_scene_instructions(
    instructions: str,
    style_instructions: str = 'N/A',
    people_descriptions: str = 'N/A',
    model: GeminiModel = _DEFAULT_SCENE_MODEL,
    client: Optional[Client] = None,
) -> str:
    LOGGER.info('Generating scene description...')
    LOGGER.debug(f'Input scene instruction: {instructions}')
    LOGGER.debug(f'Input style instructions: {style_instructions}')
    LOGGER.debug(f'Input people descriptions: {people_descriptions}')
    prompt = PROMPT.format(
        instructions=instructions,
        style_instructions=style_instructions,
        people_descriptions=people_descriptions,
    )
    description = await generate_text_response(prompt=prompt, model=model, client=client)

    LOGGER.debug(f'Generated scene description: {description}')
    return description
