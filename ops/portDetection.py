from evdev import InputDevice, list_devices

devices = map(InputDevice, list_devices())
eventX=""

for dev in devices:
    print(dev.path)
    if dev.name == "ADS7846 Touchscreen":
        eventX = dev.fn
print(eventX)