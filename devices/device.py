from abc import ABC, abstractmethod
import io
from dataclasses import dataclass
from typing import Optional


@dataclass
class FileDTO:
    data: io.BytesIO
    extension: str


@dataclass
class ImageDTO:
    jpeg: Optional[FileDTO]
    raw: Optional[FileDTO]

class Device(ABC):
    @abstractmethod
    def prepare(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def take_photo(self) -> ImageDTO:
        raise NotImplementedError
    
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

