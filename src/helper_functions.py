import pynvml
import datetime
import time
import ctypes

class UnsupportedDriverVersion(Exception):
    pass

class TemperatureThresholds:
    def __init__(self, shutdown_t, slowdown_t, max_memory_t, gpu_max_t, min_acoustic_t, current_acoustic_t, max_acoustic_t):
        self.shutdown = shutdown_t
        self.slowdown = slowdown_t
        self.max_memory = max_memory_t
        self.gpu_max = gpu_max_t
        self.min_acoustic = min_acoustic_t
        self.current_acoustic = current_acoustic_t
        self.max_acoustic = max_acoustic_t

class PowerLimitConstraintsWatts:
    def __init__(self, min_pl, max_pl):
        self.min = min_pl
        self.max = max_pl

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

def get_gpu_fan_speed_per_controller(gpu_handle):

    fan_speed_per_controller = []

    # This is not really the number of fan, but the number of controllers
    fan_count = pynvml.nvmlDeviceGetNumFans(gpu_handle)

    for fan_idx in range(fan_count):
        fan_speed_per_controller.append(pynvml.nvmlDeviceGetFanSpeed_v2(gpu_handle, fan_idx))

    return fan_speed_per_controller

# This function will be here for only future references as many drivers ignore such values
def get_gpu_fan_speed_constraints(gpu_handle):

    # It needs pointers to work
    fan_min = ctypes.c_uint(0)
    fan_max = ctypes.c_uint(0)

    # Note some drivers do not respect the minimum and may turn off the fan motor in a different speed
    # Some drivers turn off the fan motor at speeds as high as 47%
    pynvml.nvmlDeviceGetMinMaxFanSpeed(gpu_handle, ctypes.byref(fan_min), ctypes.byref(fan_max))

    return [fan_min, fan_max]

# Control GPU functions and monitor for changes (e.g. temperature)
def control_and_monitor(gpu_handle, configuration):
    
    #previous_speed = 0
    
    # Infinite loop, one must kill the process to stop it
    while(True):
        current_temp = pynvml.nvmlDeviceGetTemperature(gpu_handle, 0)
        current_speed = pynvml.nvmlDeviceGetFanSpeed(gpu_handle)

        log_helper(f'Current temp: {current_temp}°C')
        log_helper(f'Current speed: {current_speed}%') # Minitor for fan fan speed changes and reajust! 

        # Get the fan speed per controller
        for idx, fan_speed_c in enumerate(get_gpu_fan_speed_per_controller(gpu_handle)):
            log_helper(f'Fan controller {idx}: {fan_speed_c}%')

        found_temp_match = False
        for pair in configuration.temp_speed_pair:

            # Remember that that list starts by the highest temp value and keeps lowering it
            if current_temp >= pair.temperature:

                # Only send commands to the GPU if necessary (if the current setting is different from the targeted one)
                #if previous_speed != pair.speed or current_speed != pair.speed:
                if current_speed != pair.speed:
                    set_gpu_fan_speed(gpu_handle, pair.speed, configuration.dry_run)
                    #previous_speed = pair.speed
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

# Power control

# nvmlDeviceGetPowerManagementMode was deprecated: https://docs.nvidia.com/deploy/nvml-api/group__nvmlDeviceQueries.html#group__nvmlDeviceQueries_1g10365092adc37d7a17d261db8fe63fb6
# nvmlDeviceSetPowerManagementLimit_v2 also seems to be deprecated, docs are non-existent: https://docs.nvidia.com/deploy/nvml-api/nvml_8h.html#nvml_8h_1d10040f340986af6cda91e71629edb2b

def set_power_limit(gpu_handle, power_limit_watts, dry_run):

    # Setting the power limit can be DANGEROUS! Use dry run for testing before actual changes
    if dry_run != True:
        pynvml.nvmlDeviceSetPowerManagementLimit(gpu_handle, int(power_limit_watts / 1000))

# Current power limit defined by the user, but it might defer from the enforced one
def get_current_power_limit_watts(gpu_handle):
    return int(pynvml.nvmlDeviceGetPowerManagementLimit(gpu_handle) / 1000)

# This one takes the constraints into account
def get_enforced_power_limit_watts(gpu_handle):
    return int(pynvml.nvmlDeviceGetEnforcedPowerLimit(gpu_handle) / 1000)

def get_power_limit_constraints_watts(gpu_handle):
    constraints_array = pynvml.nvmlDeviceGetPowerManagementLimitConstraints(gpu_handle)
    min = int(constraints_array[0] / 1000)
    max = int(constraints_array[1] / 1000)

    return PowerLimitConstraintsWatts(min, max)


def print_power_limit_info(configuration):
    gpu_handle = get_GPU_handle_by_name(configuration.target_gpu)

    constraints = get_power_limit_constraints_watts(gpu_handle)
    current_pl = get_current_power_limit_watts(gpu_handle)
    current_enforced_pl = get_enforced_power_limit_watts(gpu_handle)

    print(f'Power limit constraints\nMin: {constraints.min}W - Max: {constraints.max}W\n')
    print(f'Current power limit: {current_pl}W\n')
    print(f'Current enforced power limit: {current_enforced_pl}W\n')

def power_control(configuration):
    pass

# Temperature control

# nvmlDeviceGetTemperatureThreshold is deprecated for some thresholds, use nvmlDeviceGetFieldValues insted
# https://docs.nvidia.com/deploy/nvml-api/group__nvmlDeviceQueries.html#group__nvmlDeviceQueries_1g271ba78911494f33fc079b204a929405
def get_temperarure_thresholds(gpu_handle):
    # Info from nvidia-settings: T.Limit temperature after which GPU may shut down for HW protection
    #shutdown_threshold = pynvml.nvmlDeviceGetFieldValues(gpu_handle, [pynvml.NVML_FI_DEV_TEMPERATURE_SHUTDOWN_TLIMIT])[0].value.siVal
    shutdown_threshold = 0

    # Info from nvidia-settings: T.Limit temperature after which GPU may begin HW slowdown
    #slowdown_threshold = pynvml.nvmlDeviceGetFieldValues(gpu_handle, [pynvml.NVML_FI_DEV_TEMPERATURE_SLOWDOWN_TLIMIT])[0].value.siVal
    slowdown_threshold = 0

    # Info from nvidia-settings: T.Limit temperature after which GPU may begin SW slowdown due to memory temperature
    #max_memory_threshold = pynvml.nvmlDeviceGetFieldValues(gpu_handle, [pynvml.NVML_FI_DEV_TEMPERATURE_MEM_MAX_TLIMIT])[0].value.siVal
    max_memory_threshold = 0

    # Info from nvidia-settings: T.Limit temperature after which GPU may be throttled below base clock
    #gpu_max_threshold = pynvml.nvmlDeviceGetFieldValues(gpu_handle, [pynvml.NVML_FI_DEV_TEMPERATURE_GPU_MAX_TLIMIT])[0].value.siVal
    gpu_max_threshold =0

    # The acoustic settings is the same used by GeForce Experience
    # Info from nvidia-settings: Current temperature that is set as acoustic threshold.
    current_acoustic_threshold = pynvml.nvmlDeviceGetTemperatureThreshold(gpu_handle, pynvml.NVML_TEMPERATURE_THRESHOLD_ACOUSTIC_CURR)
    
    # These thresholds still use the old function
    # Info from nvidia-settings: Minimum GPU Temperature that can be set as acoustic threshold
    min_acoustic_threshold = pynvml.nvmlDeviceGetTemperatureThreshold(gpu_handle, pynvml.NVML_TEMPERATURE_THRESHOLD_ACOUSTIC_MIN)

    # Info from nvidia-settings: Maximum GPU temperature that can be set as acoustic threshold.
    max_acoustic_threshold = pynvml.nvmlDeviceGetTemperatureThreshold(gpu_handle, pynvml.NVML_TEMPERATURE_THRESHOLD_ACOUSTIC_MAX)

    return TemperatureThresholds(shutdown_threshold, slowdown_threshold, max_memory_threshold, gpu_max_threshold, min_acoustic_threshold, current_acoustic_threshold, max_acoustic_threshold)

# Valid values for threshold_type
#   NVML_TEMPERATURE_THRESHOLD_SHUTDOWN 
#   NVML_TEMPERATURE_THRESHOLD_SLOWDOWN 
#   NVML_TEMPERATURE_THRESHOLD_MEM_MAX 
#   NVML_TEMPERATURE_THRESHOLD_GPU_MAX
#   NVML_TEMPERATURE_THRESHOLD_ACOUSTIC_MIN 
#   NVML_TEMPERATURE_THRESHOLD_ACOUSTIC_CURR <- only this one will be supported
#   NVML_TEMPERATURE_THRESHOLD_ACOUSTIC_MAX 
def set_temperature_thresholds(gpu_handle, threshold_type, temperature_C, dry_run):

    if dry_run != True:
        pynvml.nvmlDeviceSetTemperatureThreshold(gpu_handle, threshold_type, temperature_C)

def print_thresholds_info(configuration):

    gpu_handle = get_GPU_handle_by_name(configuration.target_gpu)

    temperarure_thresholds = get_temperarure_thresholds(gpu_handle)

    #print(f'Temperature threshold - shutdown: {temperarure_thresholds.shutdown}°C')
    #print(f'Temperature threshold - slowdown: {temperarure_thresholds.slowdown}°C')
    #print(f'Temperature threshold - max memory temperature: {temperarure_thresholds.max_memory}°C')
    #print(f'Temperature threshold - ignore base clock: {temperarure_thresholds.gpu_max}°C')
    print(f'Temperature threshold - current acoustic: {temperarure_thresholds.current_acoustic}°C')
    print(f'Temperature threshold - minimum acoustic: {temperarure_thresholds.min_acoustic}°C')
    print(f'Temperature threshold - maximum acoustic: {temperarure_thresholds.max_acoustic}°C')

def temp_control(configuration):
    pass