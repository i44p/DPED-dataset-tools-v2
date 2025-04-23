from .device import Device, ImageDTO, FileDTO
import io
from typing import Optional
import time
import scrcpy
import adbutils


class Kvadra(Device):
    def __init__(self,
                 name: str,
                 delay: float,
                 *,
                 host: str = "127.0.0.1",
                 port: int = 5037
                 ) -> None:
        super().__init__()
        self._name = name
        self._delay = delay

        self._adb_client = adbutils.AdbClient(host=host, port=port)

        self.kvadra = self._adb_client.device_list()[0]

        self._client = scrcpy.Client(device=self.kvadra)
        self._client.start(threaded=True)
    
    def prepare(self) -> None:
        width, height = self._client.resolution if self._client.resolution else (1920, 1080)

        mid_x = width // 2
        mid_y = height // 2

        self._client.control.touch(mid_x, mid_y, action=scrcpy.ACTION_DOWN)
        time.sleep(0.1)
        self._client.control.touch(mid_x, mid_y, action=scrcpy.ACTION_UP)
        time.sleep(2)

    def take_photo(self) -> ImageDTO:
        time.sleep(self._delay)
        self._client.control.keycode(scrcpy.KEYCODE_CAMERA)
        time.sleep(2)
        photo = self._pull_photo()
        self._clear_photos()
        return photo

    def _pull_photo(self) -> ImageDTO:
        photo_names = str(self.kvadra.shell("ls -1 /sdcard/DCIM/Camera/")).split('\n')
        
        jpg: Optional[io.BytesIO] = None
        raw: Optional[io.BytesIO] = None

        for name in photo_names:
            if name.endswith('.jpg'):
                jpg = io.BytesIO(self.kvadra.sync.read_bytes(f"/sdcard/DCIM/Camera/{name}"))
            if name.endswith('.dng'):
                raw = io.BytesIO(self.kvadra.sync.read_bytes(f"/sdcard/DCIM/Camera/{name}"))
        
        return ImageDTO(
            jpeg=FileDTO(data=jpg, extension="jpg") if jpg else None,
            raw=FileDTO(data=raw, extension="dng") if raw else None
        )


    def _clear_photos(self) -> None:
        self.kvadra.shell("rm /sdcard/DCIM/Camera/*")

    def __del__(self):
        if hasattr(self, "_client"):
            self._client.stop()

    @property
    def name(self) -> str:
        return self._name
