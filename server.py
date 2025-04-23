import io
import logging
from typing import Optional
from dataclasses import fields, dataclass
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from devices.device import Device, ImageDTO
from devices.kvadra import Kvadra
from devices.sony import Sony

log = logging.getLogger(__name__)


@dataclass
class DeviceImageDTO:
    device_name: str
    image: ImageDTO


class Server:
    def __init__(self, dataset_path: Path | str = "dataset/"):
        self.dataset_path = Path(dataset_path)
        self.attached_devices: dict[str, Device] = {}

    def attach(self, device: Device) -> None:
        self.attached_devices[device.name] = device
    
    def detach(self, device_name: str) -> Device | None:
        return self.attached_devices.pop(device_name)
    
    def take_photos(self) -> Optional[int]:
        device_images: list[DeviceImageDTO] = []

        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(device.prepare): name 
                for name, device in self.attached_devices.items()
            }
            for future in as_completed(futures):
                print(f"Устройство: `{futures[future]}` сфокусированно")


        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(device.take_photo): name 
                for name, device in self.attached_devices.items()
            }

            for future in as_completed(futures):
                device_name = futures[future]
                try:    
                    image = future.result()
                    device_images.append(DeviceImageDTO(device_name=device_name, image=image))
                except Exception as e:
                    log.error("Failed Take Photo from device `%s`. Exception > %s", device_name, e)
                    return None
                
            return self._safe_photo_storage(device_images)
    
    def _safe_photo_storage(self, device_images: list[DeviceImageDTO]) -> Optional[int]:
        photo_id = 0
        last_photo_id_fp = self.dataset_path / "last_photo_id"
        if last_photo_id_fp.exists():
            with open(last_photo_id_fp, "r") as file:
                photo_id = int(file.read().strip())

        # adding a new image pair to the dataset
        photo_id += 1
        for device in device_images:
            if all( [getattr(device.image, field.name) is None for field in fields(device.image)]):
                log.error("Device `%s` returned an empty image object.", device.device_name)
                return None
            
            directory_path = self.dataset_path / device.device_name

            directory_path.mkdir(exist_ok=True, parents=True)
            
            for photo_format in fields(device.image):
                photo = getattr(device.image, photo_format.name)

                if photo and photo.data:
                    file_name = f"{photo_id:05d}.{photo.extension}"
                    self._save_photo(photo.data, file_name, directory_path)

        with open(last_photo_id_fp, "w") as file:
            file.write(str(photo_id))

        return photo_id

    def _save_photo(self, img: io.BytesIO, name: str, path: Path) -> None:
        img.seek(0)
        with open(path / name, "wb") as file:
            file.write(img.read())


def main():
    kvadra = Kvadra("kvadra", 1.2)
    camera = Sony("camera", 0.0)

    server = Server()
    server.attach(kvadra)
    server.attach(camera)
    
    while True:
        input("Введи что-нибудь: ")
        server.take_photos()
    

if __name__ == '__main__':
    main()
