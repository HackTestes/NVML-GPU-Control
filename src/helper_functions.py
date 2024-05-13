import pynvml
import datetime
import time
import ctypes

class UnsupportedDriverVersion(Exception):
    pass

def check_driver_version(driver_version_str):
    major = int(driver_version_str.split('.')[0])

    if major < 520:
        raise UnsupportedDriverVersion('Driver version is lower than 520')

def log_helper(msg):
    print(f'LOG[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]: {msg}')

def print_help():
    print('HELP TEXT')

def list_gpus():
    deviceCount = pynvml.nvmlDeviceGetCount()

    for i in range(deviceCount):
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        print(f'Device {i} name : {pynvml.nvmlDeviceGetName(handle)} - UUID: {pynvml.nvmlDeviceGetUUID(handle)}')

def print_GPU_info(gpu_handle):
    log_helper(f"Driver Version: {pynvml.nvmlSystemGetDriverVersion()}")
    log_helper(f'Device name : {pynvml.nvmlDeviceGetName(gpu_handle)}')
    log_helper(f'Device UUID : {pynvml.nvmlDeviceGetUUID(gpu_handle)}')
    log_helper(f'Device fan speed : {pynvml.nvmlDeviceGetFanSpeed(gpu_handle)}%')
    log_helper(f'Temperature {pynvml.nvmlDeviceGetTemperature(gpu_handle, 0)}°C')
    log_helper(f"Fan controller count {pynvml.nvmlDeviceGetNumFans(gpu_handle)}")

def fan_control(configuration):
    gpu_handle = get_GPU_handle_by_name(configuration.target_gpu)
    print_GPU_info(gpu_handle)
    control_and_monitor(gpu_handle, configuration)

# Search for a GPU and return a handle
# This will not work if the user has more than 2 GPUs with the same name/model, use UUID for this case
def get_GPU_handle_by_name(gpu_name):
    deviceCount = pynvml.nvmlDeviceGetCount()

    for i in range(deviceCount):
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)

        if pynvml.nvmlDeviceGetName(handle) == gpu_name:
            return handle

    print(f'It was not possible to locate the target device : {gpu_name}')
    raise GpuNotFound('It was not possible to locate the device')

def set_gpu_fan_speed(gpu_handle, speed_percentage, dry_run):

    # This is not really the number of fan, but the number of controllers
    fan_count = pynvml.nvmlDeviceGetNumFans(gpu_handle)

    for fan_idx in range(fan_count):
        fan_speed = pynvml.nvmlDeviceGetFanSpeed_v2(gpu_handle, fan_idx)

        # Setting the fan speed DANGEROUS! Use dry run for testing before actual changes
        if dry_run != True:
            pynvml.nvmlDeviceSetFanSpeed_v2(gpu_handle, fan_idx, speed_percentage)


# Control GPU functions and monitor for changes (e.g. temperature)
def control_and_monitor(gpu_handle, configuration):
    
    previous_speed = 0
    
    # Infinite loop, one must kill the process to stop it
    while(True):
        current_temp = pynvml.nvmlDeviceGetTemperature(gpu_handle, 0)
        current_speed = pynvml.nvmlDeviceGetFanSpeed(gpu_handle)

        log_helper(f'Current temp: {current_temp}')
        log_helper(f'Current speed: {current_speed}') # Minitor for fan fan speed changes and reajust! 

        found_temp_match = False
        for pair in configuration.temp_speed_pair:

            # Remember that that list starts by the highest temp value and keeps lowering it
            if current_temp >= pair.temperature:

                # Only send commands to the GPU if necessary
                if previous_speed != pair.speed or current_speed != pair.speed:
                    set_gpu_fan_speed(gpu_handle, pair.speed, configuration.dry_run)
                    previous_speed = pair.speed
                    log_helper(f'Setting GPU fan speed: {pair.speed}%')
                else:
                    log_helper(f'Same as previous speed, nothing to do!')

                found_temp_match = True
                break

        # We didn't find a match, use the default speed
        if found_temp_match == False:
            set_gpu_fan_speed(gpu_handle, configuration.default_speed, configuration.dry_run)
            log_helper(f'Found no temperature match, using default fan speed: {configuration.default_speed}')

        time.sleep(configuration.time_interval)

def fan_policy_info_msg(fan_policy: int):

    if pynvml.NVML_FAN_POLICY_TEMPERATURE_CONTINOUS_SW == fan_policy:
        return 'Current fan control policy is automatic'

    elif pynvml.NVML_FAN_POLICY_MANUAL == fan_policy:
        return 'Current fan control policy is manual'

    else:
        return 'Unknown fan control policy'

def set_fan_policy(gpu_handle, policy, dry_run):

    # This is not really the number of fan, but the number of controllers
    fan_count = pynvml.nvmlDeviceGetNumFans(gpu_handle)

    for fan_idx in range(fan_count):

        # Setting the fan control policy can be DANGEROUS! Use dry run for testing before actual changes
        if dry_run != True:
            fan_speed = pynvml.nvmlDeviceSetFanControlPolicy(gpu_handle, fan_idx, policy)
            
def fan_policy(configuration):

    current_policy = ctypes.c_uint(0)
    target_fan_policy = configuration.fan_policy
    gpu_handle = get_GPU_handle_by_name(configuration.target_gpu)

    # The library unfortunately still needs pointers
    pynvml.nvmlDeviceGetFanControlPolicy_v2(gpu_handle, 0, ctypes.byref(current_policy))

    print(fan_policy_info_msg(current_policy.value))

    if target_fan_policy == 'automatic':
        set_fan_policy(gpu_handle, 0, configuration.dry_run)

    elif target_fan_policy == 'manual':
        set_fan_policy(gpu_handle, 1, configuration.dry_run)

    print('New fan control policy set sucessfully!')

    # Get the new policy
    pynvml.nvmlDeviceGetFanControlPolicy_v2(gpu_handle, 0, ctypes.byref(current_policy))
    print(fan_policy_info_msg(current_policy.value))



