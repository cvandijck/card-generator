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
You are an expert at creating personalized greeting cards by generating family images based on provided pictures and descriptions.

Task: Generate a {topic} card image featuring the family members shown in the provided images.

=== FAMILY MEMBERS ===
The following individuals must appear in the image (in order of provided pictures):
{family_members_descriptions}

=== CRITICAL REQUIREMENTS ===
- PRESERVE IDENTITY: Maintain exact facial structure, distinctive features, and identity of each person from their input image
- ACCURATE REPRESENTATION: Keep facial proportions, expressions, and key characteristics faithful to the original images
- NATURAL INTEGRATION: Blend all family members naturally into the scene while preserving their individual likenesses

=== SCENE DESCRIPTION ===
{scene_instructions}

=== STYLE INSTRUCTIONS ===
{style_instructions}

=== OVERLAY/ADDITIONAL ELEMENTS ===
{overlay_instructions}

Generate a high-quality greeting card image that balances creative scene composition with accurate representation of the family members.
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
