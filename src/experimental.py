import pynvml
import os
import subprocess
import sys
from ctypes import *


print(f'argv: {sys.argv}')
print(f"os.execv(`{sys.executable}`, {sys.argv})")
print(f"'{sys.executable}' {' '.join(sys.argv)}")

restart = input("Restart? Y/N\n")

if restart == "Y":
    print("Restarting now...")
    os.execv(sys.executable, ['python3'] + sys.argv)
    #os.system(f'"{sys.executable}" {" ".join(sys.argv)}')
    #subprocess.run([sys.executable] + sys.argv, timeout=1)
    
quit()

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