from pathlib import Path

import PIL.Image
from pydantic import BaseModel, ConfigDict


class Profile(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    image: PIL.Image.Image
    name: str
    description: str

    @classmethod
    def from_filepath(cls, path: Path, name: str, description: str) -> 'Profile':
        image = PIL.Image.open(path)
        return cls(image=image, name=name, description=description)

    def __str__(self):
        return f'Picture of {self.name}: {self.description}'


def describe_profiles(profiles: list[Profile]) -> str:
    profile_strs = '\n'.join(f'- {str(profile)}' for profile in profiles)
    return f'Profiles of {len(profiles)}:\n{profile_strs}'
