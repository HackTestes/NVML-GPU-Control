# NVML GPU Control

This is a small program that uses the NVIDIA Management Library (NVML) to monitor GPU temperature and set fan speed. NVML is being used, because it is OS and display sever agnostic (that means it doesn't depend on X11 or Windows). Another important reason is that the official NVIDIA tool (NVIDIA smi) does not currently support fan control.

## Disclaimer

* This project is NOT endorsed or sponsored by NVIDIA
* This project is independent

## Supported hardware

* Any NVIDIA CUDA supported card with a driver higher or equal to version 520

## Dependencies

To use it, you must have installed:

* NVIDIA's proprietary drivers (>= v520)
* Python 3
* [nvidia-ml-py](https://pypi.org/project/nvidia-ml-py/) (NVIDIA's official python bindings)

You will also need **admin/root** privileges to be able to **set anything**. Query can be done by unprivileged users however.

## Why I am creating this project?

Because of multiple reasons:

1. NVIDIA smi doesn't change fan speed
2. Can't use nvidia-settings under Wayland to control the fans
3. GeForce Experience needs internet to work and it's pretty bad

Now that NVIDIA added the functions to work on any CUDA supported card on drivers equal or higher than v520 (see Change Log [here](https://docs.nvidia.com/deploy/nvml-api/change-log.html#change-log)), it is possible to control GeForce cards' fans through NVML! This means that I can get perfect Wayland support as well, since NVML doesn't depend on a display server.

NVIDIA's change log
```
Changes between v515 and v520
The following new functionality is exposed on NVIDIA display drivers version 520 Production or later.
...
Added nvmlDeviceGetFanControlPolicy_v2 API to report the control policy for a specified GPU fan.
Added nvmlDeviceSetFanControlPolicy API to set the control policy for a specified GPU fan.

Changes between v510 and v515
The following new functionality is exposed on NVIDIA display drivers version 515 Production or later.
...
Added nvmlDeviceSetFanSpeed_v2 API to set the GPU's fan speed.
Added nvmlDeviceSetDefaultFanSpeed_v2 API to set the GPU's default fan speed.
Added nvmlDeviceGetThermalSettings API to report the GPU's thermal system information.
...
Added nvmlDeviceGetMinMaxFanSpeed API to report the min and max fan speed that user can set for a specified GPU fan.
```

Screenshots: [NVIDIA NVML change logs 515](img/NVIDIA_NVML_change_logs_515.jpeg), [NVIDIA NVML change logs 520](img/NVIDIA_NVML_change_logs_520.jpeg)

## Installation

### Windows

Install the package with [pip](https://packaging.python.org/en/latest/tutorials/installing-packages/) running as **admin** to make it system wide (needed for startup services)

```bash
pip install caioh-nvml-gpu-control
```

### Linux

Install the package with [pipx](https://github.com/pypa/pipx) running as root, so it can be [installed system-wide](https://pipx.pypa.io/stable/installation/#-global-argument) (needed for startup services).

```bash
sudo pipx install --global caioh-nvml-gpu-control
```

> [!WARNING]
> Files must be writable only to admin/root, otherwise unprivileged programs may escalate provileges with the startup services. If you followed the steps, this should be done already 

## Uninstall

> [!NOTE]
> To uninstall the version before the packaging, please refer to the [MANUAL_INSTALL](MANUAL_INSTALL.md)

### Windows

Uninstall the package by running [pip](https://packaging.python.org/en/latest/tutorials/installing-packages/) as **admin**

```bash
pip uninstall caioh-nvml-gpu-control
```

### Linux

Uninstall the package by running [pipx](https://github.com/pypa/pipx) command as **root**

```bash
sudo pipx uninstall --global caioh-nvml-gpu-control
```

## How to use

> [!NOTE]
> The python command on Windows may require the **.exe** at the end (like this "python.exe")

> [!TIP]
> You can start the program with `chnvml` if the Scripts directory is in the PATH or use `python -m caioh_nvml_gpu_control`.

* You must first list all cards that are connected, so you can get the name or UUID

```bash
chnvml list
```

* Then you can select a target by name

```bash
chnvml fan-control -n 'NVIDIA GeForce RTX 4080'
```

* Or by UUID

```bash
chnvml fan-control -id GPU-00000000-0000-0000-0000-000000000000
```

* And the fan speed for each temperature level (requires admin)

```bash
sudo chnvml fan-control -n 'NVIDIA GeForce RTX 4080' -sp '10:35,20:50,30:50,35:100'
```

* You could also use the `--dry-run` for testing! (no admin or root)

```bash
chnvml fan-control -n 'NVIDIA GeForce RTX 4080' -sp '10:35,20:50,30:50,35:100' --dry-run
```

* You can also revert to the original fan state by runnig the following command or *rebooting the machine*

```bash
chnvml fan-policy --auto -n 'NVIDIA GeForce RTX 4080'
```

Note that it does not current support fan curve (or linear progression), so it works on levels. Each level the temperature is verified against the configuration (higher or equal) and then set properly. Also, each temperature associated with speed is ordered automatically. (think of it as a staircase graph)

```
Temp : speed(%)

1. 40 : 100 (>=40°C - 100%)

2. 30 : 50 (>=30°C - 50%)

3. 20 : 30 (>=20°C - 30%)

4. Default speed (DS)

___________________________

41°C - 100%

21°C - 30%

19°C - Default speed

```

#### Usage actions and options

```
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
          Time period to wait before probing the GPU again. Works for all actions that run in a loop

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

```

## Startup services

Startup services allow you to start the script at system start, so you can configure it once and everything will be working automatically. To install startup services on Windows, see [SERVICES_WINDOWS](SERVICES_WINDOWS.md). And for Linux, check [SERVICES_LINUX](SERVICES_LINUX.md).

## Security considerations

### Windows

1. Having an admin prompt under the same desktop

      An opened prompt under the same desktop can receive key command from non-privileged programs, allowing any program to escalate to admin. To mitigate this it is necessary to restrict all other programs with a UI limit JobObject, create the window under a new desktop or *not create any windows on the desktop* (this is how it is done under the guide).

2. Programs that start automatically as admin must be secured against writes

      The scripts and the executables can only be written by admin users, otherwise, another program may overwrite them and gain admin rights on the machine. Please, verify the permissions set on the python executable and on the scripts (this also applies to the library nvidia-ml-py).

### Linux

1. Having an admin prompt under the same desktop (X11)

      This is a similar risk to the Windows counterpart, especially on X11/Xorg. So, if you use X11, you must create a new session under a new TTY to create an admin window; but if you use Wayland, it already isolates windows by default. Right now, no window is created.

2. Programs that start automatically as admin must be secured against writes

      Same as Windows. All of the executables and scripts must be accessible only to the root user (UID 0). I recommend to install the pynvml library with the distro's package manager.

## Development

See [DEVELOPMENT](DEVELOPMENT.md) for guindance about development or contributions.

## Support

I will be supporting this program as long as I have NVIDIA GPUs (especially because I am also dogfooding it). Don't expect new features as it has everything currently I need, but you can suggest new features that you think is useful. You can expect however bug fixes from me so my project remains compatible with the latest versions of NVML.

If I loose the need for this software (aka change my hardware), I will make sure to update this notice.