from devices.device import Device


class Server:
    def __init__(self):
        self.attached_devices: dict[str, Device] = {}

    def attach(self, device: Device) -> None:
        self.attached_devices[device.name] = device
    
    def detach(self, device_name: str) -> Device | None:
        return self.attached_devices.pop(device_name)
    
    def take_photos(self) -> None:
        for name, device in self.attached_devices.items():
            device.take_photo()


def main():
    server = Server()
    

if __name__ == '__main__':
    main()
