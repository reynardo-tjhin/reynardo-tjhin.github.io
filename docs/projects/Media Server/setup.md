---
comments: true
---

# Setup

In this page, I documented each step that I took to set up the machine. Here is a list of things that I did:

1. BIOS update
2. Installing OS: Ubuntu Server
3. Installing remote server connection: OpenSSH Server
4. Installing Nginx

## Hardware

I bought an HP Z440 workstation from eBay. It has the following specs.

- Processor: Intel(R) Xeon(R) CPU E5-2630 v3 @ 2.40 GHz
- Memory: DDR4-1866 MHz 64 GB
- GPU: NVIDIA Quadro M2000
- Storage Controllers
    - Intel(R) C600+/C220+ series chipset SATA RAID Controller
    - Intel(R) C600+/C220+ series chipset sSATA RAID Controller
- Storage: 256 GB of SSD and 1 TB of HDD

## 1. BIOS Update

The HP Z440 workstation that I received had an older BIOS version (dated around 2014). The latest BIOS version was published in 2024. This was my first time updating a BIOS and I had a good reason to update it this time. The older BIOS version does not support PCIe bifurcation. Since I am planning to have this machine as a media server, I need the PCIe bifurcation feature. Moreover, updating the BIOS to the latest version includes a security update.

I watched this YouTube video to guide me on updating the BIOS - [YouTube Link](https://www.youtube.com/watch?v=orctVrckDOc).

1. I accessed the BIOS files from this website - [HP Support](https://support.hp.com/us-en/drivers/hp-z440-workstation/6978828)
2. The HP Z440 workstation that I have is on Windows 11 Pro. There is no Windows 11 option on the website; therefore, I had to choose Windows 10 64-bit. The following steps will show that the operating system does not matter.
3. I downloaded the BIOS files. At the time of installation, the BIOS version was 02.62 Rev.A.
4. I extracted the files to the "C:\Downloads" folder.
5. I explored the files. In my case, the file downloaded was called "sp151054.exe".
6. The file "sp151054.exe" has this directory structure
```txt
<DIR>   Capsule
<DIR>   HPBIOSUPDREC
<DIR>   HPQPASSWD
<DIR>   OpticalF10Update
        History.htm
        M60_0262.BIN
        BIOS Flash.htm
        HP_Logo.gif
        HPBIOSUPDREC64.exe
        WS_Flash_Instructions.pdf
        WS_Flash_Instructions.rtf
        UEFI-NTFS-COPYING.txt
```
7. The file that I am interested in is "M60_0262.BIN" where "262" is the version number. There are instructions on how to perform the BIOS update in the file `WS_Flash_Instructions.pdf`. I referred to the "BIOS Setup Flashing" section in `WS_Flash_Instructions.pdf` to update the BIOS without depending on the OS.
8. Since I already had a spare bootable USB drive that was used to install Debian, I did not need to prepare an extra bootable drive.
9. I created the folder exactly like this in the USB drive where "D:" represents the USB drive.
```txt
D:\Hewlett-Packard\BIOS\New\M60_0262.BIN
```
10. The HP BIOS would look into this folder specifically. I matched the letters and casing exactly.
11. I rebooted the device.
12. I pressed `Esc` to go to the Startup Menu and then proceeded to the BIOS Menu > Update BIOS...
13. It prompted me to confirm whether to update the BIOS version to 262.
14. I proceeded with the BIOS update.
15. REMINDER TO SELF! DO NOT DO ANYTHING. Let the update finish.
16. After the progress bar reached 100%, it asked for a reboot. I accepted the reboot and let it come up on its own.
17. The workstation shut down and turned on by itself. AGAIN, REMINDER NOT TO DO ANYTHING and let it come up on its own.
18. I pressed `Esc` again to the Startup Menu and the BIOS version was now 262.
19. [Checking PCIe bifurcation feature] I went to Slot Settings. There was a PCIe bifurcation option on the x16 slot. This also indicated that the BIOS update was a success.

## 2. Installing Ubuntu Server

1. At the time of installation, the Ubuntu server that I downloaded was Ubuntu 26.04 LTS. I downloaded the `.iso` file.
2. I downloaded Rufus for Windows to format the USB drive and created a bootable drive.
3. Important to self: Make sure to take a backup of all the files in the USB drive.
4. I selected the USB device to make it bootable.
5. I selected the Ubuntu Server ISO.
6. I left the rest of the configurations.
7. I clicked on the "Start" button.
8. I selected the option: Write in ISO Image mode (Recommended)
9. Apparently, the image used GRUB 2.14 but the application only included the installation files for GRUB 2.12. So I selected "Yes" to connect to the Internet and attempt to download it.
10. It warned me again that the data would be destroyed. I accepted the warning and proceeded.
11. Once READY, I clicked the "Close" button (reminder to self: do not click on the "Start" button since it would repeat the whole process of making the USB drive bootable and installing the ISO file to the USB drive). I ejected the bootable drive and plugged it into the workstation.
12. I rebooted to Boot Menu to boot to the bootable USB drive.
13. I saw the GNU GRUB version 2.14 which listed the options below. I clicked on "Try or Install Ubuntu Server".
```txt
- Try or Install Ubuntu Server
- Boot from next volume
- UEFI Firmware Settings
```
14. Once everything loaded up, the first screen I saw was to select a language for the installation setup.
15. The next screen was to select the keyboard layout. I clicked ENTER to continue.
16. I chose the base for the installation: Ubuntu Server (the default install contained a curated set of packages that provided a comfortable experience for operating the server).
17. The next screen was the network configuration. As long as the machine had connection to the internet, there would not be a problem on this page.
18. Proxy configuration: I left it blank.
19. Ubuntu archive mirror configuration: I left it as it was. It would perform some tests on the mirror location and it would say "This mirror location passed tests."
20. Guided storage configuration: I had two drives already in the workstation: one was a SATA SSD and another was HDD. I was planning to install the OS to the SSD, so I had to ensure that the disk selected was the correct one. I also selected the option "set up this disk as an LVM group". Here is a nice website to explain LVM - [LVM How To](https://tldp.org/HOWTO/LVM-HOWTO/).
21. The next page was the summary of the devices.
22. Profile configuration: I picked a name and a password (for the admin/sudo user).
23. I skipped the "Enable Ubuntu Pro" option.
24. I clicked on the "Install OpenSSH server" for remote SSH connection.
25. I did not install any extra popular snaps in the server environments (like microk8s, lxd, prometheus, etc.)
26. It would say "Installation Complete!" after the installation had finished. I clicked "Reboot Now".
27. I removed the installation media (or the bootable drive) and pressed the ENTER button.
28. After the OS installation, I performed some updates using `sudo apt update` and `sudo apt upgrade` commands.
29. I ran `htop` to see the running processes and temperatures of each CPU core, and left it for a couple of minutes.

## 3. Installing and Setting up SSH

1. OpenSSH server should already be installed during the Ubuntu Server installation setup.
2. If the option was not clicked beforehand, OpenSSH server can be installed by running the following commands.
```sh
# perform a general update
sudo apt update

# openssh-client initiates outbound SSH connections
# openssh-server listens to incoming SSH connections
# technically, openssh-client does not need to be installed
sudo apt install openssh-client openssh-server
```

3. I ran `man ssh` on the server to ensure that `openssh-*` was installed successfully.
4. Note: both client and server need to be in the same local area network in order to communicate with each other.
5. The client requires the server's username, IP address and the password to connect to the server.
    - To get the username: I ran `whoami` in the server.
    - To get the IPv4 address: I ran `ip a` in the server.
        - The first part usually states the loopback address/the localhost (127.0.0.1).
        - The second part onwards shows the devices that are connected to the network. For e.g. WiFi interface usually starts with `wlan0*` or `wlp*` while ethernet interface usually starts with `en*`. Mine is `eno1` where `eno1` refers to the on-board network interface that is integrated directly to the system's motherboard while `enp`, where the `p` refers to the PCI bus, refers to the PCI-express network cards. I got the IP address from `inet 192.168.*.*`.

6. I connected to the server from my local machine by running `ssh username@ip` in my laptop's Windows terminal.
7. It would prompt for the admin's password (the server's password that was set during setup).
8. For the first connection, it would ask whether the client (I) wanted to connect to the server.
```txt
The authenticity of host '192.168.x.x (192.168.x.x)' can't be established.
ED***** key fingerprint is SHA256:***.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? 
```

9. I typed "yes" and it permanently added the fingerprint to the known hosts.
10. The result would be like
```txt
Warning: Permanently added '192.168.*.* (ED*****) to the list of known hosts.
```

11. And I was connected to the server!

!!! info Passwordless SSH Connection
    Every time I connect to the server, it will prompt for a password.
    We can connect without entering the password, but we need to copy the **ssh keys of the client** _to_ **the server** in order to let the server know that the client that is trying to reach the server is authorised.

    1. Generate an SSH key in the client if not already done so
    ```sh
    ssh-keygen -t rsa -b 4096 -f "%USERPROFILE%\.ssh\id_rsa"
    ```
    Press Enter to accept defaults, and leave the passphrase empty for auto-login

    2. Copy the key to the server
    ```sh
    ssh-copy-id -i %USERPROFILE%\.ssh\id_rsa.pub username@ip
    ```
    OR
    ```
    type %USERPROFILE%\.ssh\id_rsa.pub | ssh username@ip "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
    ```
    What it does is it will copy the key to the file ~/.ssh/authorized_keys

    3. Test the passwordless SSH login
    ```
    ssh username@ip
    ```

    4. To prevent from typing the username and IP address directly, create a batch file in the client machine.
    ```bat
    ssh username@ip
    ```
    Then create a shortcut to this batch file and place it in `C:\Users\tjhinr\AppData\Roaming\Microsoft\Windows\Start Menu\Programs` or
    `C:\ProgramData\Microsoft\Windows\Start Menu\Programs` to access it from the Windows Start Menu.

## 4. Setting up Nginx

References: 

- [nginx](https://nginx.org/en/)
- [Installing nginx on Ubuntu](https://ubuntu.com/tutorials/install-and-configure-nginx#2-installing-nginx)

Nginx is an HTTP web server, reverse proxy, content cache, load balancer, TCP/UDP proxy server and mail proxy server. Since this machine is a media server, nginx will help with serving the static files like images and streaming movies.

1. I installed nginx via the following commands
```sh
sudo apt update
sudo apt install nginx
```

2. To know that nginx was installed successfully: from my laptop that was connected to the same network as the server, I opened browser and typed in the IP address (without any port). It showed the below. The file served can also be found in this directory `/usr/share/nginx/html/index.html`.
```txt
Welcome to nginx!

If you see this page, the nginx web server is successfully installed and working. Further configuration is required.

For online documentation and support please refer to nginx.org.
Commercial support is available at nginx.com.

Thank you for using nginx.
```

3. I followed the Ubuntu tutorial to create the website using virtual host. Virtual host is a configuration within a web server that allows a single physical server to host and serve multiple distinct websites or domain names.

    Two things are needed to create the website that only serves a single file (index.html). Not the default one that Nginx already serves.
    
    1. The `index.html` file to be served to the client.
    2. The virtual host configuration file.

4. I created an `index.html` file in this directory `/var/www/tutorial/index.html`.
```html
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Hello, Nginx!</title>
</head>
<body>
    <h1>Hello, Nginx!</h1>
    <p>We have just configured our Nginx web server on Ubuntu Server!</p>
</body>
</html>
```

5. Then, I created the virtual host configuration file `tutorial` in this directory `/etc/nginx/sites-enabled/tutorial`.
```
server {
        # listen on port localhost:81
        listen 81;
        # ensures that Nginx binds specifically to the IPv6 loopback or wildcard interface
        # guarantee that the server accepts traffic on port 81 from both IPv4 and IPv6 clients
        listen [::]:81;

        # the domain name
        server_name example.ubuntu.com;

        # the directory where we placed our .html file
        root /var/www/tutorial;
        # defines the priority of index files to check
        index index.html;

        location / {
                # attempts to serve the index.html file, then returns 404
                try_files $uri $uri/ =404;
        }
}
```

6. (Extra/optional step) Afterwards, I created another `test.txt` file in this directory `/var/www/tutorial/test.txt`.
```txt
This is a text file!
If you see this file, the nginx configuration to serve static files is successful and working!
```

7. I ran the command `sudo systemctl restart nginx` to restart the nginx service.
8. In my laptop, I went to the browser and opened two new sites 
    - `192.168.*.*:81`: the contents of the `index.html` in `/var/www/tutorial/index.html`.
    - `192.168.*.*:81/test.txt`: the contents of the `test.txt` in `/var/www/tutorial/test.txt`.

9. I completed the tutorial successfully!

## Headless Server

The HP Z440 workstation came with a GPU. The CPU does not have an integrated graphics, therefore, it could not show any display. The GPU handles the display. However, since I am running this headless without any display, I don't need the GPU. But removing the GPU will produce error sounds. HP Z440 owners that removed the GPUs also faced the same problem.

Solution references:
- [YouTube Link](https://www.youtube.com/watch?v=coKPcj4xNNA&t=710s)
- [Reddit Link](https://www.reddit.com/r/homelab/comments/1it3f3o/comment/mvcuqaf/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)

1. To solve this issue, I needed to go back to the BIOS. 
2. I plugged in an external USB drive to the workstation.
3. I entered the "replicated setup" option. 
4. Then, I backed up the configuration file to the external USB drive. It would create a HPSetup.txt file and exported it to root of the USB drive.
5. I edited the file in my laptop.
    Before
    ```txt
    ...
    Internal Speaker
        Disable
        *Enable
    Headless Boot
        *Disable
        Enable
    Riser Isolation
        *Disable
        Enable
    ...
    ```
    After
    ```txt
    ...
    Internal Speaker
        Disable
        *Enable
    Headless Boot
        Disable
        *Enable
    Riser Isolation
        *Disable
        Enable
    ...
    ```
6. I saved the edited file to enable headless boot. The file should still remain in the root of the USB drive. Then I plugged back in to the workstation.
7. I entered the "replicated setup" option and uploaded the config from the USB drive.
8. I removed the USB drive and continued the boot.
9. Once I was inside the Ubuntu Server, I shut down the device using this command `sudo shutdown -h now`.
10. I removed the GPU physically and booted up the workstation again.
11. Everything worked now!