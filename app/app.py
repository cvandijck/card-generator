import asyncio
import io
import logging
from pathlib import Path

import streamlit as st
import yaml
from PIL import Image

from card_generator.genai.tools.card import generate_card
from card_generator.image.profile import ProfilePicture
from card_generator.logging import configure_logging

# UI Configuration
TEXTAREA_HEIGHT = 150


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


def main():
    """Main function to run the Streamlit app."""
    # Configure logging
    configure_logging(level=logging.INFO, exclude_external_logs=True)

    # Load configuration
    config = load_config()
    predefined_scenes = config['scenes']
    predefined_styles = config['styles']
    predefined_overlays = config['overlays']

    # Page configuration
    st.set_page_config(
        page_title='AI Card Generator',
        page_icon='🎄',
        layout='wide',
    )

    # Title and description
    st.title('🎄 AI Holiday Card Generator')
    st.markdown(
        """
        Generate personalized holiday cards using AI! Upload family photos and customize your card with descriptions,
        scene instructions, and style preferences.
        """
    )

    st.markdown('---')

    # Main content area
    col1, col2 = st.columns([1, 1], gap='large')

    with col1:
        st.header('📸 Upload Family Photos')

        # Number of family members
        num_members = st.number_input(
            'Number of family members',
            min_value=1,
            max_value=10,
            value=2,
            step=1,
        )

        family_members = []
        uploaded_files = []

        for i in range(num_members):
            st.subheader(f'Family Member {i + 1}')

            col_a, col_b = st.columns([1, 1])

            with col_a:
                uploaded_file = st.file_uploader(
                    f'Upload photo {i + 1}',
                    type=['jpg', 'jpeg', 'png'],
                    key=f'upload_{i}',
                )
                if uploaded_file:
                    uploaded_files.append(uploaded_file)
                    st.image(
                        uploaded_file,
                        caption=f'Member {i + 1}',
                        use_container_width=True,
                    )

            with col_b:
                person_name = st.text_input(
                    'Name', value=f'Person {i + 1}', key=f'name_{i}'
                )
                description = st.text_area(
                    'Description',
                    value='Family member',
                    key=f'desc_{i}',
                    height=TEXTAREA_HEIGHT,
                )

                if uploaded_file:
                    try:
                        image = Image.open(uploaded_file)
                        family_members.append(
                            {
                                'image': image,
                                'person': person_name,
                                'description': description,
                            }
                        )
                    except Exception as e:
                        st.error(f'Error loading image: {str(e)}')

    with col2:
        st.header('⚙️ Customize Your Card')
        expand_descriptions = st.checkbox(
            'Expand Profile Descriptions',
            value=True,
            help='Let AI generate more detailed descriptions of family members',
        )

        topic = st.text_input(
            'Card Topic/Theme',
            value='Holiday',
            help='The theme of your card (e.g., Holiday, Birthday, Christmas)',
        )

        # Initialize session state for presets
        if 'scene_preset' not in st.session_state:
            st.session_state.scene_preset = 'Christmas Sled Ride'
        if 'style_preset' not in st.session_state:
            st.session_state.style_preset = 'Cartoon/Comic'
        if 'overlay_preset' not in st.session_state:
            st.session_state.overlay_preset = 'Happy Holidays!'

        # Scene selection
        st.subheader('🎬 Scene')
        scene_preset = st.selectbox(
            'Choose a preset scene or create your own',
            options=list(predefined_scenes.keys()),
            index=list(predefined_scenes.keys()).index(
                st.session_state.scene_preset
            ),
            help="Select a predefined scene or choose 'Custom' to write your own",
            key='scene_preset_select',
            on_change=lambda: st.session_state.update(
                {'scene_preset': st.session_state.scene_preset_select}
            ),
        )
        st.session_state.scene_preset = scene_preset

        scene_default = predefined_scenes[scene_preset]
        scene_instructions = st.text_area(
            'Scene Instructions',
            value=scene_default,
            height=TEXTAREA_HEIGHT,
            help='Describe the scene you want in your card',
        )

        # Style selection
        st.subheader('🎨 Style')
        style_preset = st.selectbox(
            'Choose a preset style or create your own',
            options=list(predefined_styles.keys()),
            index=list(predefined_styles.keys()).index(
                st.session_state.style_preset
            ),
            help="Select a predefined style or choose 'Custom' to write your own",
            key='style_preset_select',
            on_change=lambda: st.session_state.update(
                {'style_preset': st.session_state.style_preset_select}
            ),
        )
        st.session_state.style_preset = style_preset

        style_default = predefined_styles[style_preset]
        style_instructions = st.text_area(
            'Style Instructions',
            value=style_default,
            height=TEXTAREA_HEIGHT,
            help='Describe the artistic style you want',
        )

        # Overlay selection
        st.subheader('✨ Text Overlay')
        overlay_preset = st.selectbox(
            'Choose a preset overlay or create your own',
            options=list(predefined_overlays.keys()),
            index=list(predefined_overlays.keys()).index(
                st.session_state.overlay_preset
            ),
            help="Select a predefined text overlay or choose 'Custom' to write your own",
            key='overlay_preset_select',
            on_change=lambda: st.session_state.update(
                {'overlay_preset': st.session_state.overlay_preset_select}
            ),
        )
        st.session_state.overlay_preset = overlay_preset

        overlay_default = predefined_overlays[overlay_preset]
        overlay_instructions = st.text_area(
            'Overlay/Text Instructions',
            value=overlay_default,
            height=TEXTAREA_HEIGHT,
            help='Any text or overlays to add to the image',
        )

    # Generate button
    st.markdown('---')
    if st.button('🎨 Generate Card', type='primary', use_container_width=True):
        if len(family_members) < num_members:
            st.error(
                f'Please upload all {num_members} photos before generating!'
            )
        else:
            with st.spinner(
                '✨ Generating your personalized card... This may take a minute.'
            ):
                try:
                    # Create ProfilePicture objects
                    profile_pictures = [
                        ProfilePicture(
                            image=member['image'],
                            person=member['person'],
                            description=member['description'],
                        )
                        for member in family_members
                    ]

                    # Generate the card
                    generated_image = asyncio.run(
                        generate_card(
                            family_members=profile_pictures,
                            topic=topic,
                            scene_instructions=scene_instructions,
                            overlay_instructions=overlay_instructions,
                            style_instructions=style_instructions,
                            expand_profile_descriptions=expand_descriptions,
                        )
                    )

                    # Display the result
                    st.success('🎉 Card generated successfully!')

                    # Show the generated image
                    st.header('🖼️ Your Generated Card')
                    st.image(
                        generated_image,
                        caption='Generated Holiday Card',
                        use_container_width=True,
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

                except Exception as e:
                    st.error(f'❌ Error generating card: {str(e)}')
                    st.exception(e)

    # Footer
    st.markdown('---')
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
            Made with ❤️ using Streamlit and Google Gemini AI
        </div>
        """,
        unsafe_allow_html=True,
    )


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
