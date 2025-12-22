import logging
from typing import Optional

from google.genai import Client

from card_generator.genai.google import (
    DEFAULT_TEXT_MODEL_NAME,
    GeminiModel,
    generate_text_response,
)
from card_generator.genai.tools.style_cfg import PROMPT

LOGGER = logging.getLogger(__name__)

_DEFAULT_STYLE_MODEL = GeminiModel(name=DEFAULT_TEXT_MODEL_NAME)


async def enhance_style_instructions(
    instructions: str,
    constraints: str = 'N/A',
    scene_instructions: str = 'N/A',
    profile_descriptions: str = 'N/A',
    model: GeminiModel = _DEFAULT_STYLE_MODEL,
    client: Optional[Client] = None,
) -> str:
    LOGGER.info('Generating style description...')
    LOGGER.debug(f'Input style instruction: {instructions}')
    LOGGER.debug(f'Input constraints: {constraints}')
    LOGGER.debug(f'Input scene instructions: {scene_instructions}')
    LOGGER.debug(f'Input profile descriptions: {profile_descriptions}')

    prompt = PROMPT.format(
        instructions=instructions,
        constraints=constraints,
        scene_instructions=scene_instructions,
        profile_descriptions=profile_descriptions,
    )
    description = await generate_text_response(prompt=prompt, model=model, client=client)

    LOGGER.debug(f'Generated style description: {description}')
    return description
