from pynvml import *

nvmlInit()

print(f"Driver Version: {nvmlSystemGetDriverVersion()}")


deviceCount = nvmlDeviceGetCount()


for i in range(deviceCount):
    handle = nvmlDeviceGetHandleByIndex(i)
    print(f"Device {i} : {nvmlDeviceGetName(handle)}")

    print(f"Device fan speed : {nvmlDeviceGetFanSpeed(handle)}%")
    print(f"Temperature {nvmlDeviceGetTemperature(handle, 0)}°C")

    # This is not really the number of fan, but the number of controllers
    fan_count = nvmlDeviceGetNumFans(handle)
    print(f"Fan count {fan_count}")

    for fan_idx in range(fan_count):
        fan_speed = nvmlDeviceGetFanSpeed_v2(handle, fan_idx)
        print(f"Fan {fan_idx} : {fan_speed}%")

        # Setting the fan speed DANGEROUS!
        target_fan_speed = 100
        nvmlDeviceSetFanSpeed_v2(handle, fan_idx, target_fan_speed)
        print(f"Target fan speed set: {target_fan_speed}%")


nvmlShutdown()