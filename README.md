# NVML GPU Control

This is a small program that uses the NVIDIA Management Library (NVML) to monitor GPU temperature and set fan speed. NVML is being used, because it is OS and display sever agnostic (that means it doesn't depend on X11 or Windows). Another important reason is that the official NVIDIA tool (NVIDIA smi) does not currently support fan control.

Note: this project is NOT endorsed by NVIDIA

## Supported hardware

- Any NVIDIA CUDA suported card with a driver higher or equal to version 520 

## Dependencies

To use it, you must have installed:

- NVIDIA's proprietary drivers (>= v520)
- Python 3
- [nvidia-ml-py](https://pypi.org/project/nvidia-ml-py/)

You will also need **admin/root** privileges to be able to **set the fan speed**. 

## Why I am creating this project?

Because of multiple reasons:

1. NVIDIA smi doesn't change fan speed
2. Can't use nvidia-settings under Wayland to control the fans
3. GeForce Experience needs internet to work and it's pretty bad

Now that NVIDIA added the functions to work on any CUDA supported card on drivers equal or higher than v520 (see Change Log [here](https://docs.nvidia.com/deploy/nvml-api/change-log.html#change-log)), it is possible to control GeForce cards' fans throough NVML! This means that I can get perfect Wayland support as well, since NVML doesn't depend on a display server.

## How to use

- You must first list all cards that are connected, so you can get the name

```
 python.exe .\nvml_gpu_control.py list
```

- Then you can select a target by name
```
python.exe .\nvml_gpu_control.py fan-control -t 'NVIDIA GeForce RTX 4080'
```

- And the fan speed for each termperature level 
```
sudo python.exe .\nvml_gpu_control.py fan-control -t 'NVIDIA GeForce RTX 4080' -sp '10:35,20:50,30:50,35:100'
```

- You could also use the `--dry-run` for testing! 
```
python.exe .\nvml_gpu_control.py fan-control -t 'NVIDIA GeForce RTX 4080' -sp '10:35,20:50,30:50,35:100' --dry-run
```

Note that it does not current support fan curve (or linear progression), so it works on levels. Each level the temperature is verified against the configuration (higher or equal) and then set properly. Also, each temperature associated with speed is ordered automatically. (think of it as a staricase graph)

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

#### Usage docs

```
python.exe .\nvml_gpu_control.py <ACTION> <OPTIONS>

ACTIONS
    help
          Display help text

    list
          List all available GPUs connected to the system by printing its name and UUID

    fan-control
          Monitor and controls the fan speed of the selected card (you must select a target card)


OPTIONS

    --target OR -t <GPU_NAME>
          Select a target GPU by its name

    --time-interval OR -ti <TIME_SECONDS>
          Time period to wait before probing the GPU again

    --dry-run OR -dr
          Run the program, but don't change/set anything. Useful for testing the behavior of the program

    --speed-pair OR -sp <TEMP_CELSIUS:SPEED_PERCENTAGE,TEMP_CELSIUS:SPEED_PERCENTAGE...>
          A comma separated list of pairs of temperature in celsius and the fan speed in % (temp:speed) defining basic settings for a fan curve

    --default-speed OR -ds <FAN_SPEED_PERCENTAGE>
          Set a default speed for when there is no match for the fan curve settings


```


### Setting up services (under development)

This section will present some simple commands to setup services that start as admin and run the configured program. You should secure the files under an admin only folder, so only authorized programs can modify the scripts (and DON'T use SUID in Linux).

#### Windows

Please, check MS's documentation:

- [Managing services](https://learn.microsoft.com/en-us/powershell/scripting/samples/managing-services?view=powershell-7.4)
- [Set-Service](https://learn.microsoft.com/pt-br/powershell/module/microsoft.powershell.management/set-service?view=powershell-7.4)
- [New-Service](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/new-service?view=powershell-7.4)

- [sc.exe config](https://learn.microsoft.com/pt-br/windows-server/administration/windows-commands/sc-config)


```
$params = @{
  Name = "GpuFanControl"
  BinaryPathName = 'C:\Program Files\Python312\python.exe C:\System32\GpuFanControl\nvml_gpu_control.py -t "RTX 3080" -sp 10:20,20:35:30:50,35:100'
  DisplayName = "GPU Fan Control"
  StartupType = "Automatic"
  Description = "A simple service to automatically setup NVIDIA GPU fan speed"
  Credential = $(Get-Credential -UserName 'Admin user')
}
New-Service @params -WhatIf

or 

sc.exe config 'servicename-notdisplayname' obj='\Administrator'

```

#### Linux (systemd / cronjob)

##### Systemd setup

1. Create a service file
```
[Unit]
Description=NVIDIA Fan Control service
ConditionUser=0

[Service]
Type=simple
WorkingDirectory=/
ExecStart=/usr/bin/python3 /usr/bin/nvml_gpu_control.py -t "RTX 3080" -sp 10:20,20:35:30:50,35:100
Restart=always
KillSignal=SIGQUIT

[Install]
WantedBy=multi-user.target
```