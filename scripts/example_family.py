# ruff: noqa: E501
import asyncio
import datetime
import logging
from pathlib import Path

from dotenv import load_dotenv

from card_generator.genai.tools.card import generate_card
from card_generator.genai.tools.profile import enhance_profile_descriptions
from card_generator.image.profile import Profile
from card_generator.logging import configure_logging

load_dotenv()

DATA_DIR = Path(__file__).parent / 'data'
INPUT_DIR = DATA_DIR / 'input'
OUTPUT_DIR = DATA_DIR / 'output'

SCENE_INSTRUCTIONS = """
A dramatic and exhilarating scene unfolds on a steep, pristine snow-covered hill, set during a crisp late afternoon in the heart of a vast winter wonderland. The warm, golden light of the setting sun bathes the landscape, casting long, soft shadows and sparkling highlights on the freshly fallen snow, creating a serene yet vibrant atmosphere. At the dynamic center of the composition, Christophe, Sara, Lowie, and Kamiel are captured mid-flight on a vintage wooden sled, perhaps painted a vibrant red or deep green, hurtling down the slope at breakneck speed. Christophe and Sara are depicted with comically wide-eyed expressions of sheer panic, their festive Christmas sweaters (rich reds, forest greens, and patterned wools with intricate reindeer and snowflake motifs) slightly disheveled by the wind, showcasing the rough, comforting texture of the knit. In stark contrast, young Lowie and Kamiel are radiating pure, unadulterated joy, laughing gleefully, their own colorful sweaters vibrant against the pristine white. A magnificent, thick cloud of brilliant white snow erupts around the speeding sled, frozen in a spectacular, almost explosive spray that catches the light, conveying incredible velocity and kinetic energy. In the background, a dense forest of majestic pine and fir trees, heavily laden with glistening snow, provides a deep, verdant contrast to the pristine white. Beyond the treeline, towering, craggy, snow-capped mountain peaks rise grandly against a subtly hazy, cool blue sky, adding to the epic scale and depth. The entire scene is rendered in a classical oil painting style, characterized by rich, tangible textures—from the fluffy, powdery snow and coarse wool of the sweaters to the rough bark of the trees—and bold, artistic brushwork that gives a palpable sense of movement, depth, and the crisp chill of the winter air, all captured with a slightly low, dynamic eye-level perspective to emphasize the thrilling, humorous descent and the interaction of the family with their environment.
"""

STYLE_INSTRUCTIONS = """
The artistic style is defined as a richly textured, painterly illustration in a classical oil painting medium, imbued with the grandiosity and technical skill reminiscent of the Old Masters, adapted for a vibrant, narrative greeting card aesthetic. The color treatment features a luminous and deep palette, anchored by the warm, golden hues of a late afternoon sun, complemented by cool blues in the sky and verdant forest greens, with high saturation reserved for the festive elements like crimson reds and emerald greens of the sweaters and sled, creating a harmonious interplay of warm and cool tones against the pristine, desaturated whites of the snow. Lighting and atmosphere are cinematic and dramatic, characterized by a soft, directional golden hour glow that casts long, artistic shadows and creates sparkling highlights, imbuing the scene with a serene yet exhilarating mood. Visual treatment emphasizes extraordinary tactile detail, with prominent impasto brushwork giving a palpable sense of rich textures, from the fluffy snow and coarse wool to the rough tree bark, all rendered with expressive, painterly edges and a broad tonal range that accentuates contrast and depth. Technically, the image possesses a crisp yet painterly quality, with a classical depth of field that keeps the dynamic central figures in sharp focus while maintaining detailed background elements, featuring subtle, illustrative motion blur to convey speed and kinetic energy in the erupting snow and sled, resulting in a highly polished, fine art finish suitable for a premium greeting card. The overall aesthetic draws inspiration from the dramatic lighting and textural mastery of Dutch Golden Age painting, combined with the majestic landscape grandeur of the Hudson River School, all fused into a dynamic, narrative genre piece that balances classical artistry with contemporary cheer.
"""

OVERLAY_INSTRUCTIONS = """
Overlay the image with the text "Merry Christmas!" in an elegant script font with sparkles.
"""


async def main():
    configure_logging(level=logging.DEBUG, exclude_external_logs=True)

    members_dir = INPUT_DIR / 'family'

    # define the input
    pictures = [
        Profile.from_filepath(
            path=members_dir / 'christophe.jpg',
            name='Christophe',
            description='Father',
        ),
        Profile.from_filepath(
            path=members_dir / 'sara.jpg',
            name='Sara',
            description='Mother of the family',
        ),
        Profile.from_filepath(
            path=members_dir / 'lou.jpg',
            name='Lowie',
            description='Oldest son, 5 years old',
        ),
        Profile.from_filepath(
            path=members_dir / 'mil.jpg',
            name='Kamiel',
            description='Youngest son, 3 years old.',
        ),
    ]

    updated_pictures = await enhance_profile_descriptions(pictures)

    for pic in updated_pictures:
        logging.info(f'Enhanced profile for {pic.name}: {pic.description}')

    image = await generate_card(
        profiles=updated_pictures,
        scene_instructions=SCENE_INSTRUCTIONS,
        style_instructions=STYLE_INSTRUCTIONS,
        overlay_instructions=OVERLAY_INSTRUCTIONS,
        resolution='2K',
    )
    image.save(OUTPUT_DIR / f'{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.png')


if __name__ == '__main__':
    asyncio.run(main())
