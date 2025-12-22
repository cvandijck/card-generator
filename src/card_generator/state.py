from pydantic import BaseModel, ConfigDict

from card_generator.image.profile import Profile, describe_profiles


class AppState(BaseModel):
    """Core application state."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Member profile data
    people_profiles: list[Profile] = []

    # Generation instructions
    scene_instructions: str = ''
    style_instructions: str = ''
    overlay_instructions: str = ''

    @property
    def people_descriptions(self) -> str:
        return describe_profiles(self.people_profiles)
