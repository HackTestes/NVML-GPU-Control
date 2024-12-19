import pynvml
from ctypes import *

pynvml.nvmlInit()

gpu = pynvml.nvmlDeviceGetHandleByUUID('GPU-80285976-b824-419f-d246-35946b3bb2a6')

policy = c_uint(0)

print(policy)

pynvml.nvmlDeviceGetFanControlPolicy_v2(gpu, 0, byref(policy))

print(policy)

pynvml.nvmlShutdown()