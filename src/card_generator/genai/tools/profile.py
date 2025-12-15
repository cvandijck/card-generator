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
You are an expert at creating detailed written profiles for individuals that will guide AI image generation.

Task: Analyze the provided image and optional description to create a comprehensive profile that captures:

1. Physical Characteristics:
   - Facial features (face shape, skin tone, distinctive features)
   - Hair (color, style, length, texture)
   - Eyes (color, shape, expression)
   - Age appearance and build
   - Attire and accessories

2. Expression & Demeanor:
   - Facial expression and emotional state
   - Posture and body language
   - Overall personality impression

3. Key Identity Markers:
   - Any unique or distinctive features that define this person's appearance
   - Elements critical for maintaining accurate representation

Output Requirements:
- Write as a single, flowing paragraph
- Be specific and descriptive (avoid vague terms like "nice" or "pleasant")
- Focus on visual details that an image generator needs to recreate this person accurately
- Prioritize features that maintain the person's identity and likeness

<UserProvidedDescription>
{description}
</UserProvidedDescription>

Detailed profile:
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
