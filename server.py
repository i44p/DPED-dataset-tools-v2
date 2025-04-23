import os
import io
import logging
from typing import Optional
from dataclasses import fields
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

from devices.device import Device, ImageDTO
from devices.kvadra import Kvadra
from devices.sony import MockSony

log = logging.getLogger(__name__)


@dataclass
class DeviceImageDTO:
    device_name: str
    image: ImageDTO


class Server:
    def __init__(self, dataset_path: str ="dataset/"):
        self.dataset_path = dataset_path
        self.attached_devices: dict[str, Device] = {}

    def attach(self, device: Device) -> None:
        self.attached_devices[device.name] = device
    
    def detach(self, device_name: str) -> Device | None:
        return self.attached_devices.pop(device_name)
    
    def take_photos(self) -> Optional[str]:
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
    
    def _safe_photo_storage(self, device_images: list[DeviceImageDTO]) -> Optional[str]:
        photo_id = "00000"
        temp_file = f"{self.dataset_path}.temp"
        if os.path.exists(temp_file):
            with open(temp_file, "r") as file:
                content = int(file.read())
                content += 1
                photo_id = f"{content:05d}"

        for device in device_images:
            if all( [getattr(device.image, field.name) is None for field in fields(device.image)]):
                log.error("Device `%s` returned an empty image object.", device.device_name)
                return None
            
            directory_path = f"{self.dataset_path}{device.device_name}"

            os.makedirs(directory_path, exist_ok=True)
            
            for field in fields(device.image):
                image_bytes = getattr(device.image, field.name)

                if image_bytes is not None:
                    file_name = f"{photo_id}.{field.name}"
                    self._save_photo(image_bytes, file_name, directory_path)

        with open(temp_file, "w") as file:
            file.write(photo_id)

        return photo_id

    def _save_photo(self, img: io.BytesIO, name: str, path: str) -> None:
        img.seek(0)
        with open(os.path.join(path, name), "wb") as file:
            file.write(img.read())


def main():
    kvadra = Kvadra("kvadra", 1.2)
    camera = MockSony("camera")

    server = Server()
    server.attach(kvadra)
    server.attach(camera)
    
    server.take_photos()
    

if __name__ == '__main__':
    main()
