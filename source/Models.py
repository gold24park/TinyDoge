import dataclasses

@dataclasses.dataclass
class ImageFile:
    id: int
    filename: str
    size: int
    result_size: int