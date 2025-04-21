from abc import ABC, abstractmethod
import io
from dataclasses import dataclass
from typing import Optional


@dataclass
class ImageDTO:
    jpeg: Optional[io.BytesIO]
    raw: Optional[io.BytesIO]


class Device(ABC):
    @abstractmethod
    def take_photo(self) -> ImageDTO:
        raise NotImplementedError
    
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

