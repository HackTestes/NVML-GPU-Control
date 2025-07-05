# Manual Uninstall

You only need to remove the directory (BE EXTRA CAREFUL WITH THE *RM* COMMAND). You can also use the GUI to simply delete the directory if you find that easier and safer.

Useful docs (read before running the commands):

* [Remove-Item](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/remove-item?view=powershell-7.4)
* [rm man page](https://man7.org/linux/man-pages/man1/rm.1.html)

```bash
# Windows - you can run first with the -WhatIf parameter to test 
Remove-Item -Confirm -Force -Recurse -Path 'C:\Program Files\User_NVIDIA_GPU_Control\'

# Linux
rm --interactive --preserve-root -R '/usr/bin/User_NVIDIA_GPU_Control'
```

## Services

Don't forget to remove the old startup services as well

### Windows

* Run the command in an admin prompt

```cmd
schtasks /delete /tn "User NVIDIA GPU Control Task"
```

### Linux

* Run the command as root for systemd

```bash
sudo rm -i /etc/systemd/system/unofficial-gpu-nvml-control.service
```

* Edit root's crontab (you just need to fix the command to the new one)

```bash
sudo crontab -e
```