from .device import Device, ImageDTO
import io
import os


class MockSony(Device):
    def __init__(self,
                 name: str,
                 *args
                 ) -> None:
        super().__init__()
        self._name = name


    def take_photo(self) -> ImageDTO:
        os.system("sh ./third_party/sony-camera-example-v2-linux/out/bin/shoot_an_image_and_get_it.sh")

        with open("./third_party/sony-camera-example-v2-linux/out/bin/shot.jpg", "rb") as f:
            jpg = io.BytesIO(f.read())

        photo = ImageDTO(
            jpeg=jpg,
            raw=None
        )
        return photo
        

    @property
    def name(self) -> str:
        return self._name
