from dataclasses import dataclass
from pathlib import Path

import PIL.Image


@dataclass
class ProfilePicture:
    image: PIL.Image.Image
    person: str
    description: str

    @classmethod
    def from_filepath(cls, path: Path, person: str, description: str) -> 'ProfilePicture':
        image = PIL.Image.open(path)
        return cls(image=image, person=person, description=description)

    def __str__(self):
        return f'Picture of {self.person}: {self.description}'
