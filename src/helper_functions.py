import pynvml
import datetime
import time
import ctypes

output_separator = '==============================================='

class UnsupportedDriverVersion(Exception):
    pass

class GpuNotFound(Exception):
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

class FanSpeedConstraintsPercentage:
    def __init__(self, min_s, max_s):
        self.min = min_s
        self.max = max_s

def check_driver_version(driver_version_str):
    major = int(driver_version_str.split('.')[0])

    if major < 520:
        raise UnsupportedDriverVersion('Driver version is lower than 520')

def log_helper(msg):
    print(f'LOG[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]: {msg}')

def print_help():
    help_text = '''
python ./nvml_gpu_control.py <ACTION> <OPTIONS>

ACTIONS
    help
          Display help text

    list
          List all available GPUs connected to the system by printing its name and UUID

    fan-control
          Monitor and controls the fan speed of the selected card (you must select a target card)

    fan-info
          Shows information about fan speed

    fan-policy <--auto|--manual>
          Changes the fan control policy to automatic (vBIOS controlled) or manual. Note that when the fan speed is changed, the NVML library automatically changes this setting to manual. This setting is useful to change the GPU back to its original state

    fan-policy-info
          Shows information about the current fan policy

    power-limit-info
          Shows information about the power limit of the selected GPU

    power-control
          Controls the power limit of the selected GPU. It runs in a loop by default, but can run once using the --single-use option

    thresholds-info
          Shows information about temperature thresholds in dregrees Celsius of the selected GPU.

    temp-control
          Controls the temperature thresholds configuration of the selected GPU. It runs in a loop by default, but can run once using the --single-use option

    control-all
         Allows the use of all controls in a single command/loop


OPTIONS

    --name OR -n <GPU_NAME>
          Select a target GPU by its name. Example: --name "NVIDIA GeForce RTX 4080". Note: UUID has preference over name

    --uuid OR -id <GPU_UUID>
          Select a target GPU by its Universally Unique IDentifier (UUID). Example: --uuid "GPU-00000000-0000-0000-0000-000000000000". Note: UUID has preference over name

    --time-interval OR -ti <TIME_SECONDS>
          Time period in seconds to wait before probing the GPU again. Works for all actions that run in a loop

    --retry-interval OR -ri <TIME_SECONDS>
          Time period in seconds to wait before trying to issue commands to the GPU again. Works for all actions that run in a loop

    --dry-run OR -dr
          Run the program, but don't change/set anything. Useful for testing the behavior of the program

    --speed-pair OR -sp <TEMP_CELSIUS:SPEED_PERCENTAGE,TEMP_CELSIUS:SPEED_PERCENTAGE...>
          A comma separated list of pairs of temperature in celsius and the fan speed in % (temp:speed) defining basic settings for a fan curve

    --default-speed OR -ds <FAN_SPEED_PERCENTAGE>
          Set a default speed for when there is no match for the fan curve settings

    --manual
          Sets the fan policy to manual

    --auto
          Sets the fan policy to automatic (vBIOS controlled)

    --power-limit OR -pl <POWER_LIMIT_WATTS>
          Sets the power limit of the GPU in watts

    --acoustic-temp-limit OR -tl <TEMPERATURE_CELSIUS>
          Sets the acoustic threshold in celsious (note that this is the same temperature limit used by GeForce Experience)

    --single-use OR -su
          Makes some actions work only once insted of in a loop. This option is valid for: temp-control and power-control

'''
    print(help_text)

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
    log_helper(f'Temperature {pynvml.nvmlDeviceGetTemperatureV(gpu_handle, pynvml.NVML_TEMPERATURE_GPU)}°C')
    log_helper(f"Fan controller count {pynvml.nvmlDeviceGetNumFans(gpu_handle)}")


# Search for a GPU and return a handle

def get_GPU_handle(gpu_name, gpu_uuid):
    
    if gpu_uuid != '':
        return pynvml.nvmlDeviceGetHandleByUUID(gpu_uuid)

    else:
        return get_GPU_handle_by_name(gpu_name)


# This will NOT work if the user has more than 2 GPUs with the same name/model, use UUID for this case
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

    return FanSpeedConstraintsPercentage(fan_min.value, fan_max.value)

def print_fan_info(configuration):

    gpu_handle = get_GPU_handle(configuration.gpu_name, configuration.gpu_uuid)

    current_temp = pynvml.nvmlDeviceGetTemperatureV(gpu_handle, pynvml.NVML_TEMPERATURE_GPU)
    current_speed = pynvml.nvmlDeviceGetFanSpeed(gpu_handle)
    fan_constraints = get_gpu_fan_speed_constraints(gpu_handle)

    print(f'{output_separator}')
    print(f'Current temp: {current_temp}°C')
    print(f'Current speed: {current_speed}%') # Minitor for fan fan speed changes and reajust! 

    # Get the fan speed per controller
    for idx, fan_speed_c in enumerate(get_gpu_fan_speed_per_controller(gpu_handle)):
        print(f'Fan controller speed {idx}: {fan_speed_c}%')

    print(f'Fan constraints: Min {fan_constraints.min}% - Max {fan_constraints.max}%')
    print(f'{output_separator}')

def fan_control(configuration):
    gpu_handle = get_GPU_handle(configuration.gpu_name, configuration.gpu_uuid)
    print_GPU_info(gpu_handle)

    # Infinite loop, one must kill the process to stop it
    while(True):
        fan_control_subroutine(gpu_handle, configuration)

        time.sleep(configuration.time_interval)


# Control GPU functions and monitor for changes (e.g. temperature)
def fan_control_subroutine(gpu_handle, configuration):

    current_temp = pynvml.nvmlDeviceGetTemperatureV(gpu_handle, pynvml.NVML_TEMPERATURE_GPU)
    current_speed = pynvml.nvmlDeviceGetFanSpeed(gpu_handle)

    log_helper(f'Current temp: {current_temp}°C')
    log_helper(f'Current speed: {current_speed}%') # Monitor for fan fan speed changes and reajust! 

    # Get the fan speed per controller
    for idx, fan_speed_c in enumerate(get_gpu_fan_speed_per_controller(gpu_handle)):
        log_helper(f'Fan controller speed {idx}: {fan_speed_c}%')

    for pair in configuration.temp_speed_pair:

        # Remember that that list starts by the highest temp value and keeps lowering it
        if current_temp >= pair.temperature:

            # Only send commands to the GPU if necessary (if the current setting is different from the targeted one)
            if current_speed != pair.speed:
                set_gpu_fan_speed(gpu_handle, pair.speed, configuration.dry_run)
                log_helper(f'Setting GPU fan speed: {pair.speed}%')
            else:
                log_helper(f'Same as previous speed, nothing to do!')

            # Match found and set, return now
            return

    # We didn't find a match, use the default speed
    set_gpu_fan_speed(gpu_handle, configuration.default_speed, configuration.dry_run)
    log_helper(f'Found no temperature match, using default fan speed: {configuration.default_speed}')

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

            # Also set the default fan speed for extra safety (automatic only)
            if policy == pynvml.NVML_FAN_POLICY_TEMPERATURE_CONTINOUS_SW:
                pynvml.nvmlDeviceSetDefaultFanSpeed_v2(gpu_handle, fan_idx)

def get_fan_policy(gpu_handle):
    current_policy = ctypes.c_uint(0)

    # The library unfortunately still needs pointers, this is why I need to use ctypes
    pynvml.nvmlDeviceGetFanControlPolicy_v2(gpu_handle, 0, ctypes.byref(current_policy))

    return current_policy.value

def print_fan_policy_info(configuration):
    gpu_handle = get_GPU_handle(configuration.gpu_name, configuration.gpu_uuid)
    print(f'{output_separator}')
    print(fan_policy_info_msg( get_fan_policy(gpu_handle) ))
    print(f'{output_separator}')

def fan_policy(configuration):

    target_fan_policy = configuration.fan_policy
    gpu_handle = get_GPU_handle(configuration.gpu_name, configuration.gpu_uuid)

    # Get the current policy before setting anything
    print(fan_policy_info_msg( get_fan_policy(gpu_handle) ))

    if target_fan_policy == 'automatic':
        set_fan_policy(gpu_handle, pynvml.NVML_FAN_POLICY_TEMPERATURE_CONTINOUS_SW, configuration.dry_run)

    elif target_fan_policy == 'manual':
        set_fan_policy(gpu_handle, pynvml.NVML_FAN_POLICY_MANUAL, configuration.dry_run)

    print('New fan control policy set sucessfully!')

    # Get the new policy
    print(fan_policy_info_msg( get_fan_policy(gpu_handle) ) + "\n")

# Power control

# nvmlDeviceGetPowerManagementMode was deprecated: https://docs.nvidia.com/deploy/nvml-api/group__nvmlDeviceQueries.html#group__nvmlDeviceQueries_1g10365092adc37d7a17d261db8fe63fb6
# nvmlDeviceSetPowerManagementLimit_v2 also seems to be deprecated, docs are non-existent: https://docs.nvidia.com/deploy/nvml-api/nvml_8h.html#nvml_8h_1d10040f340986af6cda91e71629edb2b

def set_power_limit(gpu_handle, power_limit_watts, dry_run):

    # Setting the power limit can be DANGEROUS! Use dry run for testing before actual changes
    if dry_run != True:
        pynvml.nvmlDeviceSetPowerManagementLimit(gpu_handle, int(power_limit_watts * 1000))

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
    gpu_handle = get_GPU_handle(configuration.gpu_name, configuration.gpu_uuid)

    constraints = get_power_limit_constraints_watts(gpu_handle)
    current_pl = get_current_power_limit_watts(gpu_handle)
    current_enforced_pl = get_enforced_power_limit_watts(gpu_handle)

    print(f'{output_separator}')
    print(f'Power limit constraints\nMin: {constraints.min}W - Max: {constraints.max}W\n')
    print(f'Current power limit: {current_pl}W\n')
    print(f'Current enforced power limit: {current_enforced_pl}W\n')
    print(f'{output_separator}')

def power_control_subroutine(gpu_handle, target_power_limit, dry_run):
    power_limit_constraints_watts = get_power_limit_constraints_watts(gpu_handle)
    current_pl = get_current_power_limit_watts(gpu_handle)
    current_enforced_pl = get_enforced_power_limit_watts(gpu_handle)

    log_helper(f'Current power limit: {current_pl}W')
    log_helper(f'Current enforced power limit: {current_enforced_pl}W')

    if target_power_limit < power_limit_constraints_watts.min or target_power_limit > power_limit_constraints_watts.max:
        log_helper(f'WARNING: trying to set power limit outside of the min({power_limit_constraints_watts.min}W) and max({power_limit_constraints_watts.max}W) range')

    if target_power_limit != current_pl or target_power_limit != current_enforced_pl:
        set_power_limit(gpu_handle, target_power_limit, dry_run)
        log_helper(f'Setting the power limit: {target_power_limit}W')

    else:
        log_helper(f'Nothing to do, current and enforced power limit is the same as the target')
    

def power_control(configuration):
    gpu_handle = get_GPU_handle(configuration.gpu_name, configuration.gpu_uuid)
    print_GPU_info(gpu_handle)

    while(True):
        power_control_subroutine(gpu_handle, configuration.power_limit, configuration.dry_run)

        if configuration.single_use == True:
            break

        time.sleep(configuration.time_interval)

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

    gpu_handle = get_GPU_handle(configuration.gpu_name, configuration.gpu_uuid)

    temperarure_thresholds = get_temperarure_thresholds(gpu_handle)

    print(f'{output_separator}')
    #print(f'Temperature threshold - shutdown: {temperarure_thresholds.shutdown}°C')
    #print(f'Temperature threshold - slowdown: {temperarure_thresholds.slowdown}°C')
    #print(f'Temperature threshold - max memory temperature: {temperarure_thresholds.max_memory}°C')
    #print(f'Temperature threshold - ignore base clock: {temperarure_thresholds.gpu_max}°C')
    print(f'Temperature threshold - current acoustic: {temperarure_thresholds.current_acoustic}°C')
    print(f'Temperature threshold - minimum acoustic: {temperarure_thresholds.min_acoustic}°C')
    print(f'Temperature threshold - maximum acoustic: {temperarure_thresholds.max_acoustic}°C')
    print(f'{output_separator}')

def temp_control_subroutine(gpu_handle, target_acoustic_temp_limit, dry_run):

    current_temp_thresholds = get_temperarure_thresholds(gpu_handle)

    log_helper(f'Current acoustic threshold: {current_temp_thresholds.current_acoustic}°C')

    if target_acoustic_temp_limit < current_temp_thresholds.min_acoustic or target_acoustic_temp_limit > current_temp_thresholds.max_acoustic:
        log_helper(f'WARNING: trying to set acoustic threshold outside of the min({current_temp_thresholds.min_acoustic}°C) and max({current_temp_thresholds.max_acoustic}°C) range')

    if target_acoustic_temp_limit != current_temp_thresholds.current_acoustic:
        set_temperature_thresholds(gpu_handle, pynvml.NVML_TEMPERATURE_THRESHOLD_ACOUSTIC_CURR, target_acoustic_temp_limit, dry_run)
        log_helper(f'Setting acoustic temperature threshold: {target_acoustic_temp_limit}°C')
    
    else:
        log_helper(f'Nothing to do, current temperature threshold is the same as the target')


def temp_control(configuration):

    gpu_handle = get_GPU_handle(configuration.gpu_name, configuration.gpu_uuid)
    print_GPU_info(gpu_handle)

    while(True):
        temp_control_subroutine(gpu_handle, configuration.acoustic_temp_limit, configuration.dry_run)

        if configuration.single_use == True:
            break

        time.sleep(configuration.time_interval)


def control_all(configuration):

    gpu_handle = get_GPU_handle(configuration.gpu_name, configuration.gpu_uuid)
    print_GPU_info(gpu_handle)

    while(True):

        # If this settings is different than the default, the user has enabled it
        if configuration.power_limit != 0:
            power_control_subroutine(gpu_handle, configuration.power_limit, configuration.dry_run)

        # If this settings is different than the default, the user has enabled it
        if configuration.acoustic_temp_limit != 0:
            temp_control_subroutine(gpu_handle, configuration.acoustic_temp_limit, configuration.dry_run)

        fan_control_subroutine(gpu_handle, configuration)

        time.sleep(configuration.time_interval)