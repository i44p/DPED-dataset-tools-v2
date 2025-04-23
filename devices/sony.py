from .device import Device, ImageDTO
import io
import os
import subprocess
from dataclasses import dataclass
import re


@dataclass
class SonyParamsDTO:
    bus: int
    dev: int


class MockSony(Device):
    def __init__(self,
                 name: str,
                 *args
                 ) -> None:
        super().__init__()
        #os.environ["LD_LIBRARY_PATH"] = "./third_party/sony-camera-example-v2-linux/out/lib"
        self._name = name
        
        self.__sony_params = self._get_sony_params()

        print("test", self.__sony_params)
        self._bus = self.__sony_params.bus
        self._dev = self.__sony_params.dev

        os.system(f"bash ./third_party/sony-camera-example-v2-linux/out/bin/0_open_session.sh --bus={self._bus} --dev={self._dev}")

    def _get_sony_params(self) -> SonyParamsDTO:
        # Выполняем команду lsusb и фильтруем результаты с помощью grep
        try:
            result = subprocess.run(['lsusb'], capture_output=True, text=True, check=True)
            sony_devices = [line for line in result.stdout.splitlines() if 'Sony' in line]

            for device in sony_devices:
                print(device)
                bus_match = re.search(r"Bus (\d+)", device)
                device_match = re.search(r"Device (\d+):", device)

                if not bus_match or not device_match:
                    raise ValueError("Failed getting sony params")
                sony_params = SonyParamsDTO(
                    bus=int(bus_match.group(1)),
                    dev=int(device_match.group(1))
                )
                return sony_params
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при выполнении команды: {e}") # Todo LOG
            


    def prepare(self) -> None:
        os.system(f"bash ./third_party/sony-camera-example-v2-linux/out/bin/1_focus_camera.sh --bus={self._bus} --dev={self._dev}")

    def take_photo(self) -> ImageDTO:
        #time.sleep()
        os.system(f"bash ./third_party/sony-camera-example-v2-linux/out/bin/3_take_photo.sh --bus={self._bus} --dev={self._dev}")

        with open("./third_party/sony-camera-example-v2-linux/out/bin/shot.jpg", "rb") as f:
            jpg = io.BytesIO(f.read())

        photo = ImageDTO(
            jpeg=jpg,
            raw=None
        )
        return photo
    
    def __del__(self) -> None:
        os.system(f"bash ./third_party/sony-camera-example-v2-linux/out/bin/4_exit_session.sh --bus={self._bus} --dev={self._dev}")
        

    @property
    def name(self) -> str:
        return self._name
