# CaioH NVML GPU Control

This is a small program that uses the NVIDIA Management Library (NVML) to monitor GPU temperature and set fan speed. NVML is being used, because it is OS and display sever agnostic (that means it doesn't depend on X11 or Windows). Another important reason is that the official NVIDIA tool (NVIDIA smi) does not currently support fan control.

## Disclaimer

* This project is NOT endorsed or sponsored by NVIDIA
* This project is independent and not affiliated to NVIDIA

## Supported hardware

* Any NVIDIA CUDA supported card with a driver higher or equal to version 520

## Dependencies

To use it, you must have installed:

* NVIDIA's proprietary drivers (>= v520)
* Python 3
* [nvidia-ml-py](https://pypi.org/project/nvidia-ml-py/) (NVIDIA's official python bindings)

You will also need **admin/root** privileges to be able to **set anything**. Query can be done by unprivileged users however.

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

    --verbose OR -V
          When there are no settings changes, leg messages are omitted by default. This option enables them back (good for debugging)

```