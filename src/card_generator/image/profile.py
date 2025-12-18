from dataclasses import dataclass
from pathlib import Path

import PIL.Image


@dataclass
class ProfilePicture:
    image: PIL.Image.Image
    description: str

    @classmethod
    def from_filepath(cls, path: Path, description: str) -> 'ProfilePicture':
        image = PIL.Image.open(path)
        return cls(image=image, description=description)
