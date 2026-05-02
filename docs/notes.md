---
date:
  created: 2026-05-02
  udpated: 2026-05-02
---

# Quick Notes

This section shows a list of commands/short notes that is useful for me to quickly grab and run them.

## Linux Commands

I have a home server (_Beelink SER5 PRO Mini PC, Ryzen 7 5850U 8C/16T(up to 4.4 GHz), 32GB DDR4 1TB PCIe3.0 SSD_) which runs Ubuntu 24.04.4 LTS (noble). Therefore, I note down the common linux commands that I use below.

| Commands | Details |
|:---------|:--------|
| `htop` | Monitor CPU usage <br> <ul><li>Install `htop`: `sudo apt install htop`</li><li>To get temperature of CPUs: `sudo apt install lm-sensors`</li><li>After running `htop`, press F2 to get to setup to show temps of CPU cores</li></ul> | 
| <ul><li>`sudo apt update`</li><li>`sudo apt list --upgradable`</li><li>`sudo apt upgrade`</li></ul> | Check for updates and upgrade the software(s) |
| `sudo dpkg -i *.deb` | Install a ".deb" package |
| `watch -n 1 nvidia-smi` | Check NVIDIA GPUs and watch them every second <br> <ul><li>Only works if `nvidia-smi` command works</li></ul> |
| <ul><li>`sudo systemctl start [service]`</li><li>`sudo systemctl stop [service]`</li><li>`sudo systemctl restart [service]`</li><li>`sudo systemctl enable [service]`</li><li>`sudo systemctl disable [service]`</li></ul> | <ul><li>Start/Stop/Restart/Enable/Disable a daemon service</li><li>Daemon services live in `/etc/systemd/system`</li></ul> |
| `scp remote-server@192.168.1.100:~/path/to/file "C:\path\to\file"` | Copy files from the Linux server to Windows host machine |
| `scp *.txt remote-server@192.168.1.100:~/path/to/file` | Copy `.txt` files from Windows host machine to Linux server |
| `lsb_release -a` | Check for Linux OS version |
| `dpkg --print-architecture` | Get the CPU architecture |
| `lscpu` | Get CPU details |
| `lspci -nn | egrep -i "3d|display|vga"` | Check for GPU presence |
| `stress-ng -cpu 24 --timeout 600s` | Run a simple CPU stress test on 24 threads <br> <ul><li>Install `stress-ng`: `sudo apt install stress-ng`</li></ul> |

## Python Commands

| Commands | Details |
|:---------|:--------|
| `pytest --cov=src tests/` | Basic `pytest` command |
| `pytest --cov=src --cov-report=html` | `pytest` command to generate HTML report |
| `python -c 'import secrets; print(secrets.token_hex())'` | Generate a random password using python secrets library |