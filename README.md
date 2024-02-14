# NVML GPU Control

This is a small program that uses the NVIDIA Management Library (NVML) to monitor GPU temperature and set fan speed. NVML is being used, because it is OS and display sever agnostic (that means it doesn't depend on X11 or Windows). Another important reason is that the official NVIDIA tool (NVIDIA smi) does not currently support fan control.

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

Now that NVIDIA added the functions to work on any CUDA supported card on drivers equal or higher than v520 (see Change Log [here](https://docs.nvidia.com/deploy/nvml-api/change-log.html#change-log)), it is possible to control GeForce cards' fans throough NVML! This means that I can get perfect Wayland support as well, since NVML doesn't depend on display server.

## How to use

- You must first list all cards that are connect

```
```

- Then you can select a target

```
```

- And the fan speed for each termperature level 
```
```

Note that it does not current support fan curve (or linear), so it works on levels. Each level the temperature is verified against the configuration (higher or equal) and then set properly. Also, each tempo associated with speed is ordered automatically.

```
Temp : speed(%)

1. 40 : 100 (>=40°C - 100%)

2. 30 : 50 (>=30°C - 50%)

3. 20 : 30 (>=20°C - 30%)

4. Default speed
___________________________

41°C - 100%

21°C - 30%

19°C - Default speed

```


### Setting up services

This section will present some simple commands to setup services that start as admin and run the configured program. 

#### Windows

Please, check MS's documentation:

- [Managing services](https://learn.microsoft.com/en-us/powershell/scripting/samples/managing-services?view=powershell-7.4)
- [Set-Service](https://learn.microsoft.com/pt-br/powershell/module/microsoft.powershell.management/set-service?view=powershell-7.4)
- [New-Service](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/new-service?view=powershell-7.4)

- [sc.exe config](https://learn.microsoft.com/pt-br/windows-server/administration/windows-commands/sc-config)


```
$params = @{
  Name = "GpuFanControl"
  BinaryPathName = 'C:\WINDOWS\System32\python3.exe -k netsvcs'
  DisplayName = "GPU Fan Control"
  StartupType = "Automatic"
  Description = "A simple service to automatically setup NVIDIA GPU fan speed"
}
New-Service @params

or 

sc.exe config 'servicename-notdisplayname' obj='\Administrator' password='secret'

```

#### Linux (systemd / cronjob)

