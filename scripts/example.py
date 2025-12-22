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
Imagine a vibrant, high-energy scene unfolding on a pristine, sun-drenched snowy slope in a majestic winter wonderland.
It's a crisp, clear mid-winter afternoon, with brilliant natural sunlight casting sharp, dynamic shadows and illuminating every sparkling snowflake with a diamond-like shimmer.
In the distance, towering, snow-capped mountains pierce an azure sky, framed by dense forests of snow-laden evergreen pine trees on the lower slopes, creating a breathtaking backdrop.

At the heart of the scene, a diverse development team, exuberantly clad in an array of humorously festive and brightly colored Christmas sweaters (some perhaps featuring pixel art, code patterns, or even subtle blinking lights), are captured mid-flight on a classic wooden sled.
The sled is hurtling down the incline with incredible velocity, creating an explosive cloud of powdery white snow that sprays dramatically outwards, engulfing the rear passengers and blurring the immediate foreground, emphasizing the exhilarating speed.
The atmosphere is one of exhilarating, slightly chaotic joy; while the team lead Christophe at the very front of the sled is depicted in a comically frantic state, wide-eyed with a mix of terror and bewildered thrill, the developers behind them are absolutely reveling in the moment,
expressions of pure delight, laughter, and high-fives frozen mid-action. One of the developers, Damon, is paraplegic, but a great skier using an adaptive sit-ski. He is not on the sled but skiing alongside it with an adaptive sit-ski.
He jumps over the sled with a big smile on his face. The lead is looking up at him while holding on for dear life. Their varied postures convey the G-forces of the ride – some leaning back in mirth, others bracing with wild abandon.
Ensure that each of the team members is distinctly recognizable, capturing their unique features and personalities, while also showcasing the camaraderie and shared exhilaration of the moment.

The composition should be dynamic, perhaps a slightly low-angle shot that emphasizes the speed and momentum of the sled as it slices diagonally across the frame, drawing the viewer's eye along its trajectory.

The color palette is a cheerful explosion of festive reds, greens, and golds from the sweaters, contrasting beautifully against the dominant cool blues and crisp whites of the snow and sky, with the deep greens of the pines adding depth.
The textures should be palpable: the soft, powdery snow, the rough wood of the sled, and the intricate knit patterns of the sweaters.
"""

STYLE_INSTRUCTIONS = """
This aesthetic embodies a **traditional painted art style** reminiscent of the **Dutch Golden Age** or **Baroque period**,
rendered specifically as an **oil painting** with a strong emphasis on the **craft of the medium**.

The **color treatment** features a rich, deep, and sophisticated palette, often anchored by warm earth tones (ochres, siennas, umbers), deep blues, and muted greens, accented with subtle, glowing highlights and profound shadows.
**Colors are generally harmonious and balanced**, with a moderate to high saturation that avoids garishness,
creating a sense of natural opulence.

**Lighting is soft, directional, and often dramatic**, employing **chiaroscuro** or **sfumato** techniques to create profound depth and form,
with light sources typically coming from a single, defined direction. **Shadows are deep, nuanced, and soft-edged**,
contributing significantly to the mood, which is typically **elegant, contemplative, and timeless**.

The **visual treatment** is characterized by a **high level of painterly detail** in focal areas,
complemented by visible, expressive **impasto brushwork** that builds up **rich, tactile textures** across surfaces.
Edges are **varied and painterly**, with some areas sharply defined and others softly blending into the background or shadows,
all contributing to a strong sense of **tonal contrast** and a wide **tonal range**.

**Technical qualities** demand a crisp, dimensional, and lush image quality, with a shallow to moderate **depth of field** to direct focus,
and an overall finish that evokes the feel of a meticulously crafted **masterpiece**, devoid of modern digital effects or filters,
ensuring an artisanal polish befitting a greeting card.

This style draws inspiration from masters like Rembrandt, Vermeer, or Titian, adapted for a warm and inviting, yet sophisticated, presentation.
"""

OVERLAY_INSTRUCTIONS = """
Overlay the image with the text "Merry Christmas!" in an elegant script font with sparkles.
"""


async def main():
    configure_logging(level=logging.DEBUG, exclude_external_logs=True)

    members_dir = INPUT_DIR / 'team'

    # define the input
    pictures = [
        Profile.from_filepath(
            path=members_dir / 'christophe2.jpg',
            name='Christophe',
            description='Team lead, ten years older then the other developers, trying to manage their energy',
        ),
        Profile.from_filepath(
            path=members_dir / 'sam2.jpg',
            name='Sam',
            description='Most senior developer, keeps a cool head, always enjoying a healthy snack of almonds on the slopes',
        ),
        Profile.from_filepath(
            path=members_dir / 'damon2.jpg',
            name='Damon',
            description='Developer. He is paraplegic, but a great skier using an adaptive sit-ski.',
        ),
        Profile.from_filepath(
            path=members_dir / 'samuel.png',
            name='Samuel',
            description='Junior developer. Loves fashion and has very noticible black moustache and wild black hair.',
        ),
        Profile.from_filepath(
            path=members_dir / 'charoun.jpg',
            name='Charoun',
            description='Business analyst. Greek and proudly so. Very stylish with a charming smile.',
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
