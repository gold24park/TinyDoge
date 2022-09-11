import dataclasses

@dataclasses.dataclass
class ImageFile:
    id: int
    filename: str
    size: int
    result_size: int

@dataclasses.dataclass
class ExitObject:
    code: int = 0
    exception: Exception = None