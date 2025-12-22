import asyncio
import io
import logging
import os
from pathlib import Path
from typing import Optional

import streamlit as st
import yaml
from dotenv import load_dotenv
from PIL import Image
from pydantic import BaseModel, ConfigDict

from card_generator.genai.tools.card import generate_card
from card_generator.genai.tools.scene import enhance_scene_instructions
from card_generator.genai.tools.style import enhance_style_instructions
from card_generator.image.profile import Profile
from card_generator.logging import configure_logging, convert_logging_level
from card_generator.state import AppState

# UI Configuration
TEXTAREA_HEIGHT = 150
LOGGER = logging.getLogger(__name__)

# Session state keys
NUM_MEMBERS = 'num_members'
SESSION_APP_STATE = 'app_state'
SESSION_SCENE_PRESET = 'scene_preset'
SESSION_STYLE_PRESET = 'style_preset'
SESSION_OVERLAY_PRESET = 'overlay_preset'
SESSION_CURRENT_MEMBER_INDEX = 'current_member_index'
SESSION_SCENE_ENHANCED = 'scene_enhanced'
SESSION_STYLE_ENHANCED = 'style_enhanced'
SESSION_MEMBERS = 'members'
SESSION_GENERATED_IMAGE = 'generated_image'

# Session state key formats (for dynamic keys)
SESSION_UPLOAD_FMT = 'upload_{}'
SESSION_NAME_FMT = 'name_{}'
SESSION_DESC_FMT = 'desc_{}'


# Load env
load_dotenv()


class PersonInput(BaseModel):
    """Input data for a person."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: Optional[str] = None
    description: Optional[str] = None
    image: Optional[Image.Image] = None


def get_app_state() -> AppState:
    """Get or initialize the app state from session."""
    if SESSION_APP_STATE not in st.session_state:
        st.session_state[SESSION_APP_STATE] = AppState()
    return st.session_state[SESSION_APP_STATE]


@st.cache_resource
def cached_configure_logging():
    # Configure logging
    log_level_str = os.getenv('LOG_LEVEL', 'WARNING').upper()
    log_level = convert_logging_level(log_level_str)
    configure_logging(level=log_level, exclude_external_logs=True)


def normalize_text(text: str) -> str:
    """Remove excessive newlines while preserving paragraph breaks."""
    if not text:
        return text
    # Replace multiple newlines with a single space, then clean up
    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    return ' '.join(cleaned_lines)


def normalize_config(config: dict) -> dict:
    """Normalize all text values in config by removing internal newlines."""
    normalized = {}
    for section, items in config.items():
        normalized[section] = {
            key: normalize_text(value) if isinstance(value, str) else value
            for key, value in items.items()
        }
    return normalized


@st.cache_data
def load_config():
    """Load configuration from YAML file."""
    config_path = Path(__file__).parent / 'config.yaml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return normalize_config(config)


def sync_member_profiles():
    app_state = get_app_state()

    member_profile_list: list[PersonInput] = st.session_state.get(SESSION_MEMBERS, [])
    num_members = st.session_state.get(NUM_MEMBERS, 0)

    required_members = member_profile_list[:num_members]

    if any(member.image is None for member in required_members):
        st.error(f'Please upload all {len(required_members)} photos before generating!')
        return

    app_state.member_profiles = [
        Profile(
            # image is ensured to be not None above
            image=member.image,  # type: ignore
            name=member.name or f'Person {idx + 1}',
            description=member.description or '',
        )
        for idx, member in enumerate(required_members)
    ]


def render_enhancement_proposal(field_key: str, proposed_text: str) -> Optional[bool]:
    """Display enhancement proposal with accept/decline buttons.

    Returns True if accepted, False if declined.
    """
    LOGGER.debug(f'Displaying enhancement proposal for {field_key}')
    st.info(f'✨ **Enhanced Version:**\n\n{proposed_text}')

    container = st.container(horizontal=True)
    with container:
        st.space(size='stretch')
        if st.button('✅ Accept', key=f'{field_key}_accept'):
            LOGGER.info(f'Accept button clicked for {field_key}')
            return True
        if st.button('❌ Decline', key=f'{field_key}_decline'):
            LOGGER.info(f'Decline button clicked for {field_key}')
            return False
        st.space(size='stretch')

    return None


def render_member_inputs():
    st.header('📸 Upload Photos')

    # Number of people
    num_members = st.number_input(
        label='Number of people in the card',
        min_value=1,
        max_value=10,
        value=2,
        step=1,
        key=NUM_MEMBERS,
    )

    if SESSION_CURRENT_MEMBER_INDEX not in st.session_state:
        st.session_state[SESSION_CURRENT_MEMBER_INDEX] = 0

    if st.session_state.get(SESSION_CURRENT_MEMBER_INDEX, 0) >= num_members:
        st.session_state[SESSION_CURRENT_MEMBER_INDEX] = num_members - 1

    # Initialize session state for all members upfront (for data persistence)
    if SESSION_MEMBERS not in st.session_state:
        st.session_state[SESSION_MEMBERS] = []

    member_profile_list: list[PersonInput] = st.session_state[SESSION_MEMBERS]
    if len(member_profile_list) < num_members:
        for _ in range(len(member_profile_list), num_members):
            member_profile_list.append(PersonInput())

    # Carousel mode: show one member at a time with navigation
    st.markdown('---')

    # Display current member
    current_member_idx = st.session_state[SESSION_CURRENT_MEMBER_INDEX]
    current_member: PersonInput = member_profile_list[current_member_idx]

    # File uploader
    uploaded_file = st.file_uploader(
        f'Upload photo {current_member_idx + 1}',
        type=['jpg', 'jpeg', 'png'],
        key=SESSION_UPLOAD_FMT.format(current_member_idx),
    )

    # Display uploaded image centrally
    if uploaded_file:
        current_member.image = Image.open(uploaded_file)

    if current_member.image:
        container = st.container(horizontal=True, horizontal_alignment='center')
        container.image(current_member.image, caption=current_member.name, width=250)

    # Input fields below the image
    # Name input - key parameter handles session state automatically
    name = st.text_input(
        label='Name',
        value=current_member.name,
        placeholder='Enter name...',
        key=SESSION_NAME_FMT.format(current_member_idx),
    )
    current_member.name = name

    # Description input with placeholder
    description = st.text_area(
        label='Description',
        value=current_member.description,
        placeholder='Describe this person...',
        key=SESSION_DESC_FMT.format(current_member_idx),
        height=TEXTAREA_HEIGHT,
    )
    current_member.description = description

    # Navigation buttons below the member fields
    st.markdown('---')
    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1], vertical_alignment='center')
    with nav_col1:
        if st.button('◀️ Previous', width='stretch', disabled=current_member_idx == 0):
            st.session_state[SESSION_CURRENT_MEMBER_INDEX] -= 1
            st.rerun()
    with nav_col2:
        st.markdown(
            f'**Person {current_member_idx + 1} of {num_members}**',
            text_alignment='center',
        )
    with nav_col3:
        if st.button('Next ▶️', width='stretch', disabled=(current_member_idx >= num_members - 1)):
            st.session_state[SESSION_CURRENT_MEMBER_INDEX] += 1
            st.rerun()


def render_customization_inputs():
    # Get application state
    app_state = get_app_state()

    # Load configuration
    config = load_config()

    predefined_scenes: dict[str, str] = config['scenes']
    predefined_styles: dict[str, str] = config['styles']
    predefined_overlays: dict[str, str] = config['overlays']

    st.header('⚙️ Customize Your Card')

    # Scene selection
    st.subheader('🎬 Scene')
    scene_options = list(predefined_scenes.keys())
    scene_selected = st.session_state.get(SESSION_SCENE_PRESET, scene_options[0])
    new_scene_preset = st.selectbox(
        label='Choose a preset scene or create your own',
        options=scene_options,
        index=scene_options.index(scene_selected),
        help="Select a predefined scene or choose 'Custom' to write your own",
    )

    # Update instructions if preset changed
    if new_scene_preset and new_scene_preset != st.session_state.get(SESSION_SCENE_PRESET):
        st.session_state[SESSION_SCENE_PRESET] = new_scene_preset
        app_state.scene_instructions = predefined_scenes[new_scene_preset]
        st.rerun()

    # Scene Instructions text area with enhancement button
    scene_col1, scene_col2 = st.columns([0.92, 0.08], gap='small', vertical_alignment='center')
    with scene_col1:
        app_state.scene_instructions = st.text_area(
            label='Scene Instructions',
            value=app_state.scene_instructions,
            height=TEXTAREA_HEIGHT,
            help='Describe the scene you want in your card',
        )
    with scene_col2:
        enhance_scene = st.button(
            label='✨',
            key='enhance_scene_btn',
            help='Enhance with AI',
            width='stretch',
        )

    if enhance_scene:
        LOGGER.debug('Enhancing scene description...')
        with st.spinner('✨ Enhancing scene description...'):
            # Gather profile descriptions for context
            sync_member_profiles()

            st.session_state[SESSION_SCENE_ENHANCED] = asyncio.run(
                enhance_scene_instructions(
                    instructions=app_state.scene_instructions,
                    style_instructions=app_state.style_instructions,
                    profile_descriptions=app_state.profile_descriptions,
                )
            )

    # Display proposal if we have enhanced text
    enhanced_scene = st.session_state.get(SESSION_SCENE_ENHANCED)
    if enhanced_scene:
        LOGGER.debug('Displaying enhancement proposal for scene')
        result = render_enhancement_proposal('scene', enhanced_scene)
        if result:
            LOGGER.info('Scene enhancement ACCEPTED - updating app_state')
            app_state.scene_instructions = enhanced_scene
            del st.session_state[SESSION_SCENE_ENHANCED]
            LOGGER.debug('Triggering rerun after scene accept')
            st.rerun()
        elif result is False:
            LOGGER.info('Scene enhancement DECLINED')
            del st.session_state[SESSION_SCENE_ENHANCED]
            st.rerun()

    # Style selection
    st.subheader('🎨 Style')
    style_options = list(predefined_styles.keys())
    style_selected = st.session_state.get(SESSION_STYLE_PRESET, style_options[0])
    new_style_preset = st.selectbox(
        label='Choose a preset style or create your own',
        options=style_options,
        index=style_options.index(style_selected),
        help="Select a predefined style or choose 'Custom' to write your own",
    )

    # Update instructions if preset changed
    if new_style_preset and new_style_preset != st.session_state.get(SESSION_STYLE_PRESET):
        st.session_state[SESSION_STYLE_PRESET] = new_style_preset
        app_state.style_instructions = predefined_styles[new_style_preset]
        st.rerun()

    # Style Instructions text area with enhancement button
    style_col1, style_col2 = st.columns([0.92, 0.08], gap='small', vertical_alignment='center')
    with style_col1:
        app_state.style_instructions = st.text_area(
            label='Style Instructions',
            value=app_state.style_instructions,
            height=TEXTAREA_HEIGHT,
            help='Describe the artistic style you want',
        )
    with style_col2:
        enhance_style = st.button(
            label='✨',
            key='enhance_style_btn',
            help='Enhance with AI',
            width='stretch',
        )

    if enhance_style:
        LOGGER.debug('Enhancing style description...')
        with st.spinner('✨ Enhancing style description...'):
            sync_member_profiles()
            st.session_state[SESSION_STYLE_ENHANCED] = asyncio.run(
                enhance_style_instructions(
                    instructions=app_state.style_instructions,
                    scene_instructions=app_state.scene_instructions,
                    profile_descriptions=app_state.profile_descriptions,
                )
            )

    # Display proposal if we have enhanced text
    enhanced_style = st.session_state.get(SESSION_STYLE_ENHANCED)
    if enhanced_style:
        LOGGER.debug('Displaying enhancement proposal for style')
        result = render_enhancement_proposal('style', enhanced_style)
        if result:
            LOGGER.info('Style enhancement ACCEPTED - updating app_state')
            app_state.style_instructions = enhanced_style
            del st.session_state[SESSION_STYLE_ENHANCED]
            LOGGER.debug('Triggering rerun after style accept')
            st.rerun()
        elif result is False:
            LOGGER.info('Style enhancement DECLINED')
            del st.session_state[SESSION_STYLE_ENHANCED]
            st.rerun()

    # Overlay selection
    st.subheader('🔤 Text Overlay')
    overlay_options = list(predefined_overlays.keys())
    overlay_selected = st.session_state.get(SESSION_OVERLAY_PRESET, overlay_options[0])
    new_overlay_preset = st.selectbox(
        'Choose a preset overlay or create your own',
        options=overlay_options,
        index=overlay_options.index(overlay_selected),
        help="Select a predefined text overlay or choose 'Custom' to write your own",
    )

    # Update instructions if preset changed
    if new_overlay_preset and new_overlay_preset != st.session_state.get(SESSION_OVERLAY_PRESET):
        st.session_state[SESSION_OVERLAY_PRESET] = new_overlay_preset
        app_state.overlay_instructions = predefined_overlays[new_overlay_preset]
        st.rerun()

    app_state.overlay_instructions = st.text_area(
        'Overlay/Text Instructions',
        value=app_state.overlay_instructions,
        height=TEXTAREA_HEIGHT,
        help='Any text or overlays to add to the image',
    )


def render_generated_image():
    if SESSION_GENERATED_IMAGE not in st.session_state:
        return

    generated_image: Image.Image = st.session_state[SESSION_GENERATED_IMAGE]

    # Show the generated image
    st.header('🖼️ Your Generated Card')
    st.image(generated_image, caption='Generated Holiday Card', width='stretch')

    # Download button
    buf = io.BytesIO()
    generated_image.save(buf, format='PNG')
    byte_im = buf.getvalue()

    st.download_button(
        label='📥 Download Card',
        data=byte_im,
        file_name='holiday_card.png',
        mime='image/png',
        width='stretch',
    )


def main():
    """Main function to run the Streamlit app."""
    cached_configure_logging()
    app_state = get_app_state()

    # Page configuration
    st.set_page_config(page_title='AI Card Generator', page_icon='🎄', layout='wide')

    # Title and description
    st.title('🎄 AI Holiday Card Generator')
    st.markdown(
        'Generate personalized holiday cards using AI! Upload family photos and customize '
        'your card with descriptions, scene instructions, and style preferences.'
    )

    st.markdown('---')

    # Main content area
    col1, col2 = st.columns([1, 1], gap='large')
    with col1:
        render_member_inputs()
    with col2:
        render_customization_inputs()

    # Generate button
    st.markdown('---')
    if st.button('🎨 Generate Card', type='primary', width='stretch'):
        # Validate all photos are uploaded
        sync_member_profiles()

        with st.spinner('✨ Generating your personalized card... This may take a minute.'):
            try:
                # Generate the card
                generated_image = asyncio.run(
                    generate_card(
                        profiles=app_state.member_profiles,
                        scene_instructions=app_state.scene_instructions,
                        overlay_instructions=app_state.overlay_instructions,
                        style_instructions=app_state.style_instructions,
                    )
                )
                st.session_state[SESSION_GENERATED_IMAGE] = generated_image

                # Display the result
                st.success('🎉 Card generated successfully!')

            except Exception as e:
                st.error(f'❌ Error generating card: {str(e)}')
                st.exception(e)

    render_generated_image()

    # Footer
    st.space(size='large')
    st.markdown(':grey[Made with ❤️]', text_alignment='center')


if __name__ == '__main__':
    import sys

    # Check if we're being run directly (not via streamlit CLI)
    if 'streamlit.web.cli' not in sys.modules:
        # Run via streamlit CLI programmatically
        from streamlit.web import cli as stcli

        sys.argv = ['streamlit', 'run', __file__]
        sys.exit(stcli.main())
    else:
        # Already running via streamlit, just call main
        main()
