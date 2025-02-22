import pynvml
from ctypes import *

pynvml.nvmlInit()

gpu = pynvml.nvmlDeviceGetHandleByUUID('GPU-80285976-b824-419f-d246-35946b3bb2a6')

#policy = c_uint(0)
#print(policy)
#
#pynvml.nvmlDeviceGetFanControlPolicy_v2(gpu, 0, byref(policy))
#print(policy)

sensors = pynvml.nvmlDeviceGetThermalSettings(gpu, 2)

for sensor in sensors:
    print(f"Controller: {sensor.controller}")
    print(f"defaultMinTemp: {sensor.controller}")
    print(f"defaultMaxTemp: {sensor.controller}")
    print(f"currentTemp: {sensor.controller}")
    print(f"target: {sensor.controller}")

temp = pynvml.nvmlDeviceGetTemperatureV(gpu, 0)
print(f"nvmlDeviceGetTemperatureV: {temp}")

temp = pynvml.nvmlDeviceGetTemperatureV1(gpu, 0)
print(f"nvmlDeviceGetTemperatureV1: {temp}")

pynvml.nvmlShutdown()