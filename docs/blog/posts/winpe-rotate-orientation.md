---
title: The Struggles of Rotating the Screen in WinPE
slug: winpe-rotate-orientation-struggles
date: 2026-05-31
categories:
  - WinPE
description: The struggles of trying to rotate the Screen from landscape to portrait orientation in WinPE
comments: true
---

# The Struggles of Rotating the Screen in WinPE

I frequently use WinPE at work to perform image backups and deployment. Some devices come with a horizontal screen while some have a vertical screen. The problem is that the orientation cannot be rotated in the WinPE environment. So I went on an arduous journey to find ways to rotate the screen in the WinPE environment. TLDR: it failed. But the seniors at work presented a different solution.

<!-- more -->

## What's WinPE

Learn more about WinPE [here](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/winpe-intro).

WinPE is a lightweight Windows OS used to install, deploy and repair Windows desktop editions, Windows Server and other Windows operating systems. WinPE is used because it is easy to create a snapshot of a hard drive and deploy the same snapshot to a device that has similar tech specs, such as the same CPU, RAM size, etc. At work, I have to support thousands of machines in production. It is very time-consuming to install Windows Server edition from scratch onto these machines. Moreover, more applications need to be installed after installing the Windows Server OS. 

Therefore, it is easier to install the applications and configure the settings on a machine with similar specs in a test lab and then take a snapshot of the hard drive (and save it as an image). This saved image can then be deployed across the thousands of machines in production.

## The Issue

The problem is that some machines have a vertical screen. Even in the boot screen, they are set to horizontal mode. Therefore, the screen is also in horizontal mode (or landscape mode) in the WinPE environment. While it does not affect our work, it is very annoying for us to tilt our heads to navigate the screen. Sometimes, I need to perform certain operations in the terminal in WinPE. It is very easy to make mistakes when working on the screen that is disorienting.

The solution is to just rotate it. Very easy idea but no...

## Possible Fix 1: A Couple of Screen Rotation EXE Applications

The first thing that came to my mind was that the EXE application in the WinPE was outdated. So I downloaded a couple of screen rotation EXE applications and copied them into the WinPE environment. After booting the device into the WinPE environment, I ran all the EXE applications. All of them failed with an error message that was similar to "...not supported...". 

I thought of a couple of issues:

1. the OS is incompatible with the EXE applications
2. missing drivers

I started from the OS. I checked using

- powershell: `Get-WmiObject -Class Win32_Processor | Select-Object Name, Architecture`
    
    Below is the meaning behind the value of each architecture number.
    
    - `0`: `x86 (32-bit)`
    - `1`: `MIPS`
    - `2`: `Alpha`
    - `3`: `PowerPC`
    - `6`: `Itanium-based`
    - `9`: `x64 (64-bit)`
    - `default`: `Unknown`

- command prompt: `echo %PROCESSOR_ARCHITECTURE%`

Both outputs reflected x86 architecture. I double-checked all the EXE applications I downloaded and all of them were for x86 architecture. So, it wasn't the OS. Therefore, I concluded that it was due to the missing drivers.

## Possible Fix 2: Intel Graphics Drivers

I paused dealing with this issue because it was not a priority for our team to work on. When my manager gave me this task again, the WinPE version was newer. The error messages were slightly more robust. Before delving into the issue, I needed to understand how an OS would rotate a screen. I sent a question prompt to Claude and it verified my gut feeling. 

Rotating a screen requires the graphics drivers. The reason is that the display is primarily supported by the GPUs since they are able to perform multiple calculations to render a screen. The machines that I work with do not have a discrete GPU. They use an Intel CPU with graphics integrated into the CPU. Hence, while in the WinPE environment, I started looking into the issue by checking whether any drivers were loaded.

In the terminal 

1. `pnputil /enum-devices` lists all the devices that the WinPE environment can see
2. `pnputil /enum-drivers` lists all the drivers installed in the WinPE environment
3. `pnputil /enum-devices /class Display` lists the display device

From the output, I learned that the WinPE environment can see the Display device but it was using the basic Windows graphics drivers to run the display. However, I didn't see any intel graphics drivers installed. So I went to get the device ID to download the appropriate Intel driver from the web.

PowerShell command: `Get-CimInstance -ClassName Win32_VideoController`

Get the `PNPDeviceID`. It should start with `PCI\VEN`. Then, I searched the web with that Device ID and downloaded the Intel drivers. After the download finished, I extracted them to a folder. The next process required me to load or inject the driver to the WIM image.

1. Copy the WinPE USB's `boot.wim` (can be found in the `sources` folder) to the Windows machine (e.g. `C:\Users\Public\MOUNT_FILE`)
2. Create another directory to store the original `boot.wim` : `mkdir C:\Users\Public\MOUNT_FILE\original`
3. Create a mount directory: `mkdir C:\Users\Public\MOUNT_FILE\mount`
4. At this point, we should have
    
    ```
    Directory of C:\Users\Public\MOUNT_FILE
    
    <DIR>  mount
    <DIR>  original
           <FILE> boot.wim  <-- the original boot.wim
    <FILE> boot.wim
    ```
    
5. Mount the WinPE image - it will extract and load the `boot.wim` into the `mount` folder
    - `DISM /Mount-Image /ImageFile:"C:\Users\Public\MOUNT_FILE\boot.wim" /Index:1 /MountDir:"C:\Users\Public\MOUNT_FILE\mount"`
    - You will see mount structure like the following
    
    ```
    Directory of C:\Users\Public\MOUNT_FILE\mount
    
    <DIR>  Program Files
    <DIR>  Program Files (x86)  <-- only if it's "x86" architecture
    <DIR>  Program Data
    <DIR>  Users
    <DIR>  Windows
    ```
    
6. Set the scratch space to the maximum (512 MB) (cannot be greater than 512 MB)
    - `DISM /Image:"C:\Users\Public\MOUNT_FILE\mount" /Set-ScratchSpace:512`
7. Inject the `inf` driver
    - `DISM /Image:"C:\Users\Public\MOUNT_FILE\mount" /Add-Driver /Driver:"C:\IntelDriver\Graphics" /Recurse`
    - Check at `C:\Users\Public\MOUNT_FILE\mount\Windows\System32\DriverStore\FileRepository\igdlh64.*` and see if there are all the files needed to run/load the drivers
8. Unmount the image
    - `DISM /Unmount-Image /MountDir:"C:\Users\Public\MOUNT_FILE\mount" /Commit`

I restarted the device and booted into the WinPE environment. I ran the 3 commands previously to check on the display device and whether the drivers were loaded: `pnputil /enum-devices`, `pnputil /enum-drivers` and `pnputil /enum-devices /class Display`. To my horror, the issue still persisted but I saw a new error code - problem 18. 

To verify I ran `pnputil /enum-devices /problem 18` and it showed the following.

```txt
Device Manager:
Problem Code: 18 (CM_PROB_REINSTALL)
Problem Status: 0xc0000493
Message: Reinstall the drivers for this device
```

I concluded that the drivers were installed but they were probably not the right ones. Then, I thought that in normal Windows, I could rotate the screen from the Windows Display settings. So, I should be able to just grab the intel drivers from the Windows OS directly... 

1. I booted into the Windows OS, went to PowerShell and ran the following: `Get-CimInstance -ClassName Win32_VideoController`. 
2. I took note of the `InfFilename` and ran `pnputil /enum-drivers /class Display` to get the `Original Name`. 
3. Since I wasn't sure where the `.inf` file might be, I ran a search in `C:\Windows` using the following command: `dir /s /b "C:\Windows" | find /I <the inf file>`. 
    I discovered that drivers are stored in `C:\Windows\System32\DriverStore\FileRepository`.

4. Then, I exported the driver: `pnputil /export-driver <the inf filename> C:\Temp`

    Edit: I just realised that I could just write the `oem*.inf` instead of the original name.

5. After exporting the right driver, I performed the same steps to inject the driver into the `boot.wim`.

I rebooted the device and went to the WinPE environment. To my absolute nightmare, it didn't work. `pnputil /enum-devices /problem 18` still showed that the device had a Problem 18. So, the drivers were installed, and even with the right drivers, the issue still persisted. The more I tried, the more I realised what WinPE was designed for. The WinPE environment is supposed to be lightweight. If it is lightweight, then it will not have the necessary software to support the graphics drivers. I reported my learnings to my manager and we decided to call it a day on this issue and revisit it another day.

## Afterword

Although I could not solve this issue, I still learned a lot from the experience. I was not satisfied without a clear answer, so I turned to my senior colleagues for help. They explained that it would require a lot of effort just to set up the WinPE environment to allow for the screen rotation feature. At the end of the day, it would be nice to have, but not worth the effort. Therefore, they suggested that since all of us work with our in-house application that runs on WinPE, we should focus on rotating the application itself. His suggestion was simple but spot on. I did not expect the suggestion at all. I guess that's what separates juniors from seniors. A colleague of mine came up with that solution too. So, my friend already thinks at a senior level 😂.
