# Linux boot services

## Setting up boot services or tasks

> [!CAUTION]
> You should secure the files under an admin only folder, so only authorized programs can modify the scripts (and DON'T use SUID on Linux with this program)

This section will present some simple commands to setup services or tasks that start as admin and run the configured program with the configured settings.

### Linux (systemd / Crontab)

This section will show how to install a global (system wide) systemd service in Ubuntu and enable it, so every time the computer starts the control will resume their work. It also shows an alternative using crontabs.

#### Systemd service

1. Take a look at the systemd service at `linux_config/caioh-gpu-nvml-control.service`. Change the GPU name and the settings to the desired configuration (Note: you can use the UUID as well).

2. Copy the unit file into `/etc/systemd/system/` (needs root)

```bash
sudo cp ./linux_config/caioh-gpu-nvml-control.service /etc/systemd/system/
```

3. Enable the service (needs root)

```bash
sudo systemctl enable --now caioh-gpu-nvml-control.service
```

4. Troubleshoot if needed (get the stdout from the service)

```bash
sudo journalctl -u caioh-gpu-nvml-control.service
```

Reload systemd daemon

```bash
sudo systemctl daemon-reload
```

#### Crontab (contributed by user on Reddit: [Brockar](https://www.reddit.com/r/wayland/comments/1arjtxj/comment/my4yfio/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button) / [@brockar](https://github.com/brockar))

1. Edit root's crontab (this ensures that the command will run as root)

```bash
sudo crontab -e
```

2. Add the command (make the changes you want here)

```bash
@reboot /usr/bin/python3 -m caioh_nvml_gpu_control -n "GPU_NAME" -pl 290 -tl 65 -sp "0:50,36:55,40:75,45:100"
```
