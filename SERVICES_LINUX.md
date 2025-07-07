# Linux startup services

## Setting up startup services

> [!CAUTION]
> You should secure the files under an admin only folder, so only authorized programs can modify the scripts (and DON'T use SUID on Linux with this program)

This section will present some simple commands to setup services that start as root and run the program with the configured settings.

### Systemd service

The next steps will show how to install a global (system wide) systemd service and enable it. Such steps were only tested on a Ubuntu machine.

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

To remove the service, you only need to delete the file

```bash
sudo rm -i /etc/systemd/system/caioh-gpu-nvml-control.service
```

### Crontab (contributed by user on Reddit: [Brockar](https://www.reddit.com/r/wayland/comments/1arjtxj/comment/my4yfio/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button) / [@brockar](https://github.com/brockar))

1. Edit root's crontab (this ensures that the command will run as root)

```bash
sudo crontab -e
```

2. Add the command (make the changes you want here)

```bash
@reboot chnvml -n "GPU_NAME" -pl 290 -tl 65 -sp "0:50,36:55,40:75,45:100"
```
