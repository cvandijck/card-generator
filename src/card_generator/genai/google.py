import logging
import os
from enum import StrEnum
from io import BytesIO
from typing import Literal, Optional

import PIL
import PIL.Image
from google.genai import Client
from google.genai.types import (
    GenerateContentConfig,
    GoogleSearch,
    ImageConfig,
    Tool,
)
from PIL.Image import Image
from pydantic import BaseModel, Field

from card_generator.genai import GEMINI_API_KEY_KEY

LOGGER = logging.getLogger(__name__)

AspectRatio = Literal['1:1', '2:3', '3:2', '3:4', '4:3', '4:5', '5:4', '9:16', '16:9', '21:9']
Resolution = Literal['1K', '2K', '4K']


class GeminiModelName(StrEnum):
    GEMINI_2_5_FLASH = 'gemini-2.5-flash'
    GEMINI_3_PRO_IMAGE_PREVIEW = 'gemini-3-pro-image-preview'


DEFAULT_TEXT_MODEL_NAME = GeminiModelName.GEMINI_2_5_FLASH
DEFAULT_IMAGE_MODEL_NAME = GeminiModelName.GEMINI_3_PRO_IMAGE_PREVIEW


class GeminiModelParameters(BaseModel):
    temperature: float = Field(default=0, ge=0, le=1)


class GeminiModel(BaseModel):
    name: GeminiModelName
    parameters: GeminiModelParameters = Field(default_factory=GeminiModelParameters)


def create_client(api_key: Optional[str] = None):
    if not api_key:
        api_key = os.environ.get(GEMINI_API_KEY_KEY)

    if not api_key:
        raise ValueError(f'{GEMINI_API_KEY_KEY} environment variable not set.')

    return Client(api_key=api_key)


async def generate_text_response(
    prompt: str,
    model: GeminiModel,
    system_prompt: Optional[str] = None,
    image_content: Optional[list[Image]] = None,
    client: Optional[Client] = None,
) -> str:
    LOGGER.info('Generating text response...')

    if client is None:
        client = create_client()

    response = await client.aio.models.generate_content(
        model=model.name,
        contents=[prompt, *(image_content or [])],
        config=GenerateContentConfig(
            response_modalities=['TEXT'],
            system_instruction=system_prompt,
        ),
    )

    if not response.text:
        raise RuntimeError('No text response generated')

    return response.text


async def generate_image_response(
    prompt: str,
    model: GeminiModel,
    system_prompt: Optional[str] = None,
    image_content: Optional[list[Image]] = None,
    aspect_ratio: AspectRatio = '1:1',
    resolution: Resolution = '1K',
    add_grounding: bool = False,
    client: Optional[Client] = None,
) -> Image:
    LOGGER.info('Generating image response...')

    if client is None:
        client = create_client()

    tools = []
    if add_grounding:
        tools.append(Tool(google_search=GoogleSearch()))

    response = await client.aio.models.generate_content(
        model=model.name,
        contents=[prompt, *(image_content or [])],
        config=GenerateContentConfig(
            response_modalities=['IMAGE'],
            system_instruction=system_prompt,
            tools=tools,
            image_config=ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=resolution,
            ),
        ),
    )
    parts = response.parts
    if not parts:
        raise RuntimeError('No image response generated')

    images = [part.as_image() for part in parts if part.inline_data is not None]
    images = list(filter(None, images))

    if not images:
        raise RuntimeError('No image response generated')
    if len(images) > 1:
        LOGGER.warning('Multiple images generated, returning only the first')

    if not images[0].image_bytes:
        raise RuntimeError('No image data available in the response')

    return PIL.Image.open(BytesIO(images[0].image_bytes))
