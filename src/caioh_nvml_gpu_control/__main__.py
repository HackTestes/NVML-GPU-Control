import sys
import os

# If we run the script from main (like python -m or directly from script), the other scripts might not find the imports
# So we add the dir where __main__ resides as an import path
# This also helps to keep the rest of the code clean
sys.path.append(os.path.dirname( os.path.realpath(__file__) ))

import nvml_gpu_control

# Call from python -m
if __name__ == '__main__':
    nvml_gpu_control.main()

# Call from script entrypoint
def script_call():
    nvml_gpu_control.main()