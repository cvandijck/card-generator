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
from pydantic import BaseModel, ConfigDict, Field

from card_generator.genai import GEMINI_API_KEY_KEY
from card_generator.genai.tools.card import generate_card
from card_generator.genai.tools.scene import enhance_scene_instructions
from card_generator.genai.tools.style import enhance_style_instructions
from card_generator.image.profile import ProfilePicture
from card_generator.logging import configure_logging, convert_logging_level

# UI Configuration
TEXTAREA_HEIGHT = 150
LOGGER = logging.getLogger(__name__)

# Session state keys
SESSION_APP_STATE = 'app_state'
SESSION_SCENE_PRESET = 'scene_preset'
SESSION_STYLE_PRESET = 'style_preset'
SESSION_OVERLAY_PRESET = 'overlay_preset'
SESSION_ENHANCING_SCENE = 'enhancing_scene'
SESSION_ENHANCING_STYLE = 'enhancing_style'
SESSION_CURRENT_MEMBER_INDEX = 'current_member_index'
SESSION_SCENE_ENHANCED = 'scene_enhanced'
SESSION_STYLE_ENHANCED = 'style_enhanced'
SESSION_FAMILY_MEMBERS = 'family_members'
SESSION_GENERATED_IMAGE = 'generated_image'

# Session state key formats (for dynamic keys)
SESSION_UPLOAD_FMT = 'upload_{}'
SESSION_NAME_FMT = 'name_{}'
SESSION_DESC_FMT = 'desc_{}'


# Load env
load_dotenv()


class AppState(BaseModel):
    """Core application state."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Family member profile data
    family_members: list[ProfilePicture] = Field(default_factory=list)

    # Generation instructions
    topic: str = ''
    scene_instructions: str = ''
    style_instructions: str = ''
    overlay_instructions: str = ''


class FamilyMemberInput(BaseModel):
    """Input data for a family member."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    image: Optional[Image.Image] = None
    name: Optional[str] = None
    description: Optional[str] = None

    @property
    def is_complete(self) -> bool:
        """Check if all fields are filled."""
        return self.image is not None and bool(self.name) and bool(self.description)


def get_app_state() -> AppState:
    """Get or initialize the app state from session."""
    if SESSION_APP_STATE not in st.session_state:
        st.session_state[SESSION_APP_STATE] = AppState()
    return st.session_state[SESSION_APP_STATE]


def init_ui_state():
    """Initialize UI-specific session state (presets, enhancement flags)."""
    if SESSION_SCENE_PRESET not in st.session_state:
        st.session_state[SESSION_SCENE_PRESET] = 'Christmas Sled Ride'
    if SESSION_STYLE_PRESET not in st.session_state:
        st.session_state[SESSION_STYLE_PRESET] = 'Cartoon/Comic'
    if SESSION_OVERLAY_PRESET not in st.session_state:
        st.session_state[SESSION_OVERLAY_PRESET] = 'Happy Holidays!'
    if SESSION_ENHANCING_SCENE not in st.session_state:
        st.session_state[SESSION_ENHANCING_SCENE] = False
    if SESSION_ENHANCING_STYLE not in st.session_state:
        st.session_state[SESSION_ENHANCING_STYLE] = False
    if SESSION_CURRENT_MEMBER_INDEX not in st.session_state:
        st.session_state[SESSION_CURRENT_MEMBER_INDEX] = 0
    if SESSION_FAMILY_MEMBERS not in st.session_state:
        st.session_state[SESSION_FAMILY_MEMBERS] = []


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


def load_config():
    """Load configuration from YAML file."""
    config_path = Path(__file__).parent / 'config.yaml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return normalize_config(config)


def display_enhancement_proposal(field_key: str, proposed_text: str) -> Optional[bool]:
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


def main():
    """Main function to run the Streamlit app."""
    cached_configure_logging()

    # Load configuration
    config = load_config()

    st.sidebar.title('🔑 API Key Configuration')
    gemini_key = st.sidebar.text_input(
        label='Gemini API Key',
        value=os.getenv(GEMINI_API_KEY_KEY, ''),
        key=GEMINI_API_KEY_KEY,
        type='password',
    )

    if not gemini_key:
        st.sidebar.error('Please enter your Gemini API Key to continue.')

    predefined_scenes = config['scenes']
    predefined_styles = config['styles']
    predefined_overlays = config['overlays']

    # Get application state
    app_state = get_app_state()
    init_ui_state()

    # Initialize default instructions if empty
    if not app_state.scene_instructions:
        app_state.scene_instructions = predefined_scenes[st.session_state.scene_preset]
    if not app_state.style_instructions:
        app_state.style_instructions = predefined_styles[st.session_state.style_preset]
    if not app_state.overlay_instructions:
        app_state.overlay_instructions = predefined_overlays[st.session_state.overlay_preset]

    # Page configuration
    st.set_page_config(
        page_title='AI Card Generator',
        page_icon='🎄',
        layout='wide',
    )

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
        st.header('📸 Upload Family Photos')

        # Number of family members
        num_members = st.number_input(
            label='Number of family members',
            min_value=1,
            max_value=10,
            value=2,
            step=1,
        )

        # Reset current_member_index if num_members changed
        if st.session_state[SESSION_CURRENT_MEMBER_INDEX] >= num_members:
            st.session_state[SESSION_CURRENT_MEMBER_INDEX] = 0

        # Initialize session state for all members upfront (for data persistence)
        family_member_list: list[FamilyMemberInput] = st.session_state[SESSION_FAMILY_MEMBERS]
        if len(family_member_list) < num_members:
            for _ in range(len(family_member_list), num_members):
                family_member_list.append(FamilyMemberInput())

        # Carousel mode: show one member at a time with navigation
        st.markdown('---')

        # Display current member
        current_member_idx = st.session_state[SESSION_CURRENT_MEMBER_INDEX]
        current_member: FamilyMemberInput = family_member_list[current_member_idx]

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
            container.image(
                current_member.image,
                caption=st.session_state.get(
                    SESSION_NAME_FMT.format(current_member_idx), f'Member {current_member_idx + 1}'
                ),
                width=250,
            )

        # Input fields below the image
        # Name input - key parameter handles session state automatically
        name = st.text_input(
            'Name',
            value=current_member.name,
            key=SESSION_NAME_FMT.format(current_member_idx),
            placeholder='Enter name...',
        )
        current_member.name = name

        # Description input with placeholder
        description = st.text_area(
            'Description',
            value=current_member.description,
            placeholder='Describe this family member...',
            key=SESSION_DESC_FMT.format(current_member_idx),
            height=TEXTAREA_HEIGHT,
        )
        current_member.description = description

        # Navigation buttons below the member fields
        st.markdown('---')
        nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1], vertical_alignment='center')

        if nav_col1.button('◀️ Previous', width='stretch', disabled=current_member_idx == 0):
            st.session_state[SESSION_CURRENT_MEMBER_INDEX] -= 1
            st.rerun()

        nav_col2.markdown(
            f'**Family Member {current_member_idx + 1} of {num_members}**',
            text_alignment='center',
        )

        if nav_col3.button(
            'Next ▶️', width='stretch', disabled=(current_member_idx >= num_members - 1)
        ):
            st.session_state[SESSION_CURRENT_MEMBER_INDEX] += 1
            st.rerun()

    with col2:
        st.header('⚙️ Customize Your Card')

        app_state.topic = st.text_input(
            'Card Topic/Theme',
            value=app_state.topic or 'Holiday',
            help='The theme of your card (e.g., Holiday, Birthday, Christmas)',
        )

        # Scene selection
        st.subheader('🎬 Scene')
        new_scene_preset = st.selectbox(
            'Choose a preset scene or create your own',
            options=list(predefined_scenes.keys()),
            index=list(predefined_scenes.keys()).index(st.session_state[SESSION_SCENE_PRESET]),
            help="Select a predefined scene or choose 'Custom' to write your own",
        )

        # Update instructions if preset changed
        if new_scene_preset and new_scene_preset != st.session_state[SESSION_SCENE_PRESET]:
            st.session_state[SESSION_SCENE_PRESET] = new_scene_preset
            app_state.scene_instructions = predefined_scenes[new_scene_preset]
            st.rerun()

        # Scene Instructions label
        st.markdown('**Scene Instructions**')

        # Scene Instructions text area with enhancement button
        scene_col1, scene_col2 = st.columns([0.92, 0.08], gap='small')
        with scene_col1:
            app_state.scene_instructions = st.text_area(
                'label',
                value=app_state.scene_instructions,
                height=int(TEXTAREA_HEIGHT * 1.5),
                help='Describe the scene you want in your card',
                label_visibility='collapsed',
            )
        with scene_col2:
            if st.button(
                '✨',
                key='enhance_scene_btn',
                help='Enhance with AI',
                width='stretch',
            ):
                LOGGER.info('Scene enhancement button clicked')
                st.session_state[SESSION_ENHANCING_SCENE] = True

        # Show enhancement proposal if requested
        if st.session_state[SESSION_ENHANCING_SCENE]:
            LOGGER.info('Entering scene enhancement block')
            # Only call API if we don't have cached enhanced text
            if SESSION_SCENE_ENHANCED not in st.session_state:
                with st.spinner('✨ Enhancing scene description...'):
                    try:
                        LOGGER.debug('Calling enhance_scene_instructions...')
                        enhanced = asyncio.run(
                            enhance_scene_instructions(app_state.scene_instructions)
                        )
                        LOGGER.info('Scene enhancement completed.')
                        if enhanced:
                            st.session_state[SESSION_SCENE_ENHANCED] = enhanced
                        else:
                            st.error('Failed to enhance scene description')
                            st.session_state[SESSION_ENHANCING_SCENE] = False
                    except Exception as e:
                        st.error(f'Error enhancing scene: {str(e)}')
                        LOGGER.error(f'Scene enhancement error: {str(e)}', exc_info=True)
                        st.session_state[SESSION_ENHANCING_SCENE] = False

            # Display proposal if we have enhanced text
            if SESSION_SCENE_ENHANCED in st.session_state:
                LOGGER.debug('Displaying enhancement proposal for scene')
                result = display_enhancement_proposal(
                    'scene', st.session_state[SESSION_SCENE_ENHANCED]
                )
                if result is True:
                    LOGGER.info('Scene enhancement ACCEPTED - updating app_state')
                    app_state.scene_instructions = st.session_state[SESSION_SCENE_ENHANCED]
                    st.session_state[SESSION_ENHANCING_SCENE] = False
                    del st.session_state[SESSION_SCENE_ENHANCED]
                    LOGGER.debug('Triggering rerun after scene accept')
                    st.rerun()
                elif result is False:
                    LOGGER.info('Scene enhancement DECLINED')
                    st.session_state[SESSION_ENHANCING_SCENE] = False
                    del st.session_state[SESSION_SCENE_ENHANCED]

        # Style selection
        st.subheader('🎨 Style')
        new_style_preset = st.selectbox(
            'Choose a preset style or create your own',
            options=list(predefined_styles.keys()),
            index=list(predefined_styles.keys()).index(st.session_state[SESSION_STYLE_PRESET]),
            help="Select a predefined style or choose 'Custom' to write your own",
        )

        # Update instructions if preset changed
        if new_style_preset and new_style_preset != st.session_state[SESSION_STYLE_PRESET]:
            st.session_state[SESSION_STYLE_PRESET] = new_style_preset
            app_state.style_instructions = predefined_styles[new_style_preset]
            st.rerun()

        # Style Instructions label
        st.markdown('**Style Instructions**')

        # Style Instructions text area with enhancement button
        style_col1, style_col2 = st.columns([0.92, 0.08], gap='small')
        with style_col1:
            app_state.style_instructions = st.text_area(
                'label',
                value=app_state.style_instructions,
                height=TEXTAREA_HEIGHT,
                help='Describe the artistic style you want',
                label_visibility='collapsed',
            )
        with style_col2:
            if st.button(
                '✨',
                key='enhance_style_btn',
                help='Enhance with AI',
                width='stretch',
            ):
                LOGGER.info('Style enhancement button clicked')
                st.session_state[SESSION_ENHANCING_STYLE] = True

        # Show enhancement proposal if requested
        if st.session_state[SESSION_ENHANCING_STYLE]:
            LOGGER.info('Entering style enhancement block')
            # Only call API if we don't have cached enhanced text
            if SESSION_STYLE_ENHANCED not in st.session_state:
                with st.spinner('✨ Enhancing style description...'):
                    try:
                        LOGGER.debug('Calling enhance_style_instructions...')
                        enhanced = asyncio.run(
                            enhance_style_instructions(app_state.style_instructions)
                        )
                        LOGGER.info('Style enhancement completed.')
                        if enhanced:
                            st.session_state[SESSION_STYLE_ENHANCED] = enhanced
                        else:
                            st.error('Failed to enhance style description')
                            st.session_state[SESSION_ENHANCING_STYLE] = False
                    except Exception as e:
                        st.error(f'Error enhancing style: {str(e)}')
                        LOGGER.error(f'Style enhancement error: {str(e)}', exc_info=True)
                        st.session_state[SESSION_ENHANCING_STYLE] = False

            # Display proposal if we have enhanced text
            if SESSION_STYLE_ENHANCED in st.session_state:
                LOGGER.debug('Displaying enhancement proposal for style')
                result = display_enhancement_proposal(
                    'style', st.session_state[SESSION_STYLE_ENHANCED]
                )
                if result is True:
                    LOGGER.info('Style enhancement ACCEPTED - updating app_state')
                    app_state.style_instructions = st.session_state[SESSION_STYLE_ENHANCED]
                    st.session_state[SESSION_ENHANCING_STYLE] = False
                    del st.session_state[SESSION_STYLE_ENHANCED]
                    LOGGER.debug('Triggering rerun after style accept')
                    st.rerun()
                elif result is False:
                    LOGGER.info('Style enhancement DECLINED')
                    st.session_state[SESSION_ENHANCING_STYLE] = False
                    del st.session_state[SESSION_STYLE_ENHANCED]

        # Overlay selection
        st.subheader('✨ Text Overlay')
        new_overlay_preset = st.selectbox(
            'Choose a preset overlay or create your own',
            options=list(predefined_overlays.keys()),
            index=list(predefined_overlays.keys()).index(st.session_state[SESSION_OVERLAY_PRESET]),
            help="Select a predefined text overlay or choose 'Custom' to write your own",
        )

        # Update instructions if preset changed
        if new_overlay_preset and new_overlay_preset != st.session_state[SESSION_OVERLAY_PRESET]:
            st.session_state[SESSION_OVERLAY_PRESET] = new_overlay_preset
            app_state.overlay_instructions = predefined_overlays[new_overlay_preset]
            st.rerun()

        app_state.overlay_instructions = st.text_area(
            'Overlay/Text Instructions',
            value=app_state.overlay_instructions,
            height=TEXTAREA_HEIGHT,
            help='Any text or overlays to add to the image',
        )

    # Generate button
    st.markdown('---')
    if st.button('🎨 Generate Card', type='primary', width='stretch'):
        # Validate all photos are uploaded
        family_member_list = st.session_state[SESSION_FAMILY_MEMBERS]
        if not all(member.is_complete for member in family_member_list):
            st.error(f'Please upload all {num_members} photos before generating!')
        else:
            # Populate family_members from session state
            app_state.family_members = []
            for j in range(num_members):
                upload_key = SESSION_UPLOAD_FMT.format(j)
                name_key = SESSION_NAME_FMT.format(j)
                desc_key = SESSION_DESC_FMT.format(j)

                if upload_key in st.session_state and st.session_state[upload_key] is not None:
                    try:
                        image = Image.open(st.session_state[upload_key])
                        person_name = st.session_state.get(name_key, f'Person {j + 1}')
                        description = st.session_state.get(desc_key, '')

                        app_state.family_members.append(
                            ProfilePicture(
                                image=image,
                                person=person_name,
                                description=description,
                            )
                        )
                    except Exception as e:
                        st.error(f'Error loading image for member {j + 1}: {str(e)}')
                        break

            with st.spinner('✨ Generating your personalized card... This may take a minute.'):
                try:
                    # Generate the card
                    generated_image = asyncio.run(
                        generate_card(
                            family_members=app_state.family_members,
                            topic=app_state.topic,
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

    generated_image = st.session_state.get(SESSION_GENERATED_IMAGE)
    if generated_image:
        # Show the generated image
        st.header('🖼️ Your Generated Card')
        st.image(
            generated_image,
            caption='Generated Holiday Card',
            width='stretch',
        )

        # Download button
        buf = io.BytesIO()
        generated_image.save(buf, format='PNG')
        byte_im = buf.getvalue()

        st.download_button(
            label='📥 Download Card',
            data=byte_im,
            file_name='holiday_card.png',
            mime='image/png',
            use_container_width=True,
        )

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
