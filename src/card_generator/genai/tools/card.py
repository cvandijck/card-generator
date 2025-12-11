import asyncio
import logging
from typing import Optional

from google.genai import Client
from PIL.Image import Image

from card_generator.genai.google import (
    GeminiModel,
    GeminiModelName,
    generate_image_response,
)
from card_generator.genai.tools.profile import (
    generate_profile_description,
)
from card_generator.image.profile import ProfilePicture

LOGGER = logging.getLogger(__name__)

_DEFAULT_MODEL = GeminiModel(name=GeminiModelName.GEMINI_3_PRO_IMAGE_PREVIEW)
_PROMPT = """
You are an expert at creating personalized greeting cards by generating fun and festive family images
based on provided pictures and descriptions. Create a fun family image to be used as a {topic} card.

You are provided with pictures of each family member. The family consists of (in the order of the provided pictures):
{family_members_descriptions}

General instructions:
- Maintain the exact facial structure, identity, and key features of the persons in the input images

The scene to be depicted is as follows:
{scene_instructions}

The picture should be styled according to the following instructions:
{style_instructions}

Additionally, apply the following overlay instructions to the image:
{overlay_instructions}

"""


async def generate_card(
    family_members: list[ProfilePicture],
    topic: str,
    scene_instructions: str,
    overlay_instructions: Optional[str] = None,
    style_instructions: Optional[str] = None,
    expand_profile_descriptions: bool = False,
    model: GeminiModel = _DEFAULT_MODEL,
    client: Optional[Client] = None,
) -> Image:
    LOGGER.info('Generating card image...')

    if expand_profile_descriptions:
        coroutines = [
            generate_profile_description(
                image=pic.image,
                description=pic.description,
                client=client,
            )
            for pic in family_members
        ]
        expanded_descriptions = await asyncio.gather(*coroutines)
        family_member_descriptions = '\n'.join(expanded_descriptions)
    else:
        family_member_descriptions = '\n'.join(
            [f'- {str(pic)}' for pic in family_members]
        )

    if not overlay_instructions:
        overlay_instructions = 'N/A'

    if not style_instructions:
        style_instructions = 'Photorealistic style with vibrant colors.'

    prompt = _PROMPT.format(
        topic=topic,
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
