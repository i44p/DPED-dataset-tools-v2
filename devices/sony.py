import io
import os
import time
import subprocess

from .device import Device, ImageDTO, FileDTO


class MockSony(Device):
    def __init__(self,
                 name: str,
                 delay: float,
                 *args,
                 usb_device_id: str = '054c:0994'
                 ) -> None:
        super().__init__()
        #os.environ["LD_LIBRARY_PATH"] = "./third_party/sony-camera-example-v2-linux/out/lib"
        self._name = name
        self._delay = delay
        self._usb_device_id = usb_device_id

        self._bus = 0
        self._dev = 0
        self._autodetect_usb_device()

        os.system(f"bash ./third_party/sony-camera-example-v2-linux/out/bin/0_open_session.sh --bus={self._bus} --dev={self._dev}")

    def _run(self, *args) -> subprocess.CompletedProcess[str]:
        return subprocess.run(args, capture_output=True, text=True, check=True)

    def _autodetect_usb_device(self) -> None:
        try:
            device_entry = self._run('lsusb', '-d', self._usb_device_id).stdout.splitlines()[0]
            _, bus, _, dev, *_ = device_entry.split()

            self._bus = int(bus)
            self._dev = int(dev.rstrip(':'))
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при выполнении команды: {e}") # Todo LOG

    def prepare(self) -> None:
        os.system(f"bash ./third_party/sony-camera-example-v2-linux/out/bin/1_focus_camera.sh --bus={self._bus} --dev={self._dev}")

    def take_photo(self) -> ImageDTO:
        time.sleep(self._delay)
        os.system(f"bash ./third_party/sony-camera-example-v2-linux/out/bin/3_take_photo.sh --bus={self._bus} --dev={self._dev}")

        with open("./third_party/sony-camera-example-v2-linux/out/bin/shot.jpg", "rb") as f:
            jpg = io.BytesIO(f.read())
        
        with open("./third_party/sony-camera-example-v2-linux/out/bin/shot.arw", "rb") as f:
            raw = io.BytesIO(f.read())

        photo = ImageDTO(
            jpeg=FileDTO(data=jpg, extension="jpg"),
            raw=FileDTO(data=raw, extension="raw")
        )
        return photo
    
    def __del__(self) -> None:
        os.system(f"bash ./third_party/sony-camera-example-v2-linux/out/bin/4_exit_session.sh --bus={self._bus} --dev={self._dev}")        

    @property
    def name(self) -> str:
        return self._name
