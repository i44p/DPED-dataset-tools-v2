from .device import Device, ImageDTO
import io
import os


class MockSony(Device):
    def __init__(self,
                 name: str,
                 *args
                 ) -> None:
        super().__init__()
        #os.environ["LD_LIBRARY_PATH"] = "./third_party/sony-camera-example-v2-linux/out/lib"
        self._name = name

        self._bus = 3
        self._dev = 45

        os.system(f"sh ./third_party/sony-camera-example-v2-linux/out/bin/0_open_session.sh --bus={self._bus} --dev={self._dev}")

    def prepare(self) -> None:
        os.system(f"sh ./third_party/sony-camera-example-v2-linux/out/bin/1_focus_camera.sh --bus={self._bus} --dev={self._dev}")

    def take_photo(self) -> ImageDTO:
        time.sleep()
        os.system(f"sh ./third_party/sony-camera-example-v2-linux/out/bin/3_take_photo.sh --bus={self._bus} --dev={self._dev}")

        with open("./third_party/sony-camera-example-v2-linux/out/bin/shot.jpg", "rb") as f:
            jpg = io.BytesIO(f.read())

        photo = ImageDTO(
            jpeg=jpg,
            raw=None
        )
        return photo
    
    def __del__(self) -> None:
        os.system(f"sh ./third_party/sony-camera-example-v2-linux/out/bin/4_exit_session.sh --bus={self._bus} --dev={self._dev}")
        

    @property
    def name(self) -> str:
        return self._name
