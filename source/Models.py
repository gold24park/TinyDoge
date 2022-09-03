import dataclasses

@dataclasses.dataclass
class ImageFile:
    filename: str
    size: int
    result_size: int