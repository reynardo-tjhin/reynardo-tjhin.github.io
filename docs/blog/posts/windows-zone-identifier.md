---
title: Windows Zone.Identifier
slug: windows-zone-identifier
date: 2026-07-09
categories:
  - Miscellaneous
description: Windows Zone.Identifier Files
comments: true
---

# Windows Zone.Identifier

This blog post explains what Windows Zone.Identifiers are, how they interfered with my job, and how to remove them.

<!-- more -->

## The Scenario

I had to copy some installation files to another folder to perform a software update via a batch script. However, the device's security application prevented the installation files from being copied. The log did not complain. Windows also logged the error level of the command, but the error level indicated 0, meaning the command reported success even though the copy actually failed.

```txt
"Thu 07/09/2026 12:00:00.00 - Copy new_update.software to update folder" 
    0 file(s) copied.
```

We typically use our in-house monitoring server to push software updates to Kiosk machines. However, we were preparing a disk image at the time — a snapshot of a hard drive that can be loaded onto new devices instead of installing Windows and performing multiple updates from scratch. This preserves all the configurations and updates that have been performed. Because the monitoring server would overwrite the image state, we had to use a USB drive instead.

Here is the timeline of the update process.

1. Logged off the user from the current Kiosk application
2. Logged in as the admin user
3. Lowered the security level of the security application
4. Copied the `new_update.software` file to `C:\Temp\Software Update\update` folder from a USB
5. Raised the security level of the security application
6. Rebooted the Kiosk
7. The `startup.bat` from the Kiosk automatically ran during startup and copied the `new_update.software` to the folder `C:\Program Files (x86)\Security Application\update`. Copying the file directly to the folder is not allowed (even for administrators). That is the reason why we copied to `C:\Temp\Software Update\update` folder in step 4.
8. **Step 7 failed to copy**.
9. Software update failed.

I concluded that it was not Windows or the script's problem. It had something to do with the device's security application. Upon looking at the security application's logs, it showed the following (the line was lengthy, so I only took the important details).

```txt
Timestamp: 2026-07-09 12:00:00,000
Status: D (Denied)
Owner: NT AUTHORITY\SYSTEM
Program: C:\WINDOWS\SYSWOW64\CMD.EXE
File: C:\Program Files (x86)\Security Application\update\new_update.software:Zone.Identifier:$DATA
Action: NtCreateFile
User: cust_mvmonitoring_ps
```

The file path showed extra information: `Zone.Identifier:$DATA`. Initially, we thought the command was written incorrectly because of this extra data. We tried different commands and strategies, such as using robocopy, renaming files before copying, and more. However, none of these strategies worked.

## The Breakthrough

As a workaround, we tried downloading the software update file from the monitoring server directly to the `C:\Temp\Software Update\update` folder and rebooted the Kiosk machine. The software update succeeded.

What made this different?

- Both copies used the same destination folder
- Both copies used the same file
- Both copies were triggered by the same script

The only difference was the source of the file. The first attempt used a USB drive. The second attempt used the monitoring server. Since the `new_update.software` file was originally downloaded from the monitoring server to a computer before being placed on the USB, this pointed to the Zone.Identifier being attached to the file during the original download. Windows treats files downloaded from a server as originating from an external source and automatically attaches the Zone.Identifier metadata. The USB itself is trusted and does not introduce the Zone.Identifier — the file already carried it. That is when we focused on the `Zone.Identifier:$DATA` clue from the security log.

## What Is Zone.Identifier?

This webpage explains Windows Zone Identifiers very well — [What is Zone.Identifier (Windows)? Meaning, Purpose, and How to Remove It Safely](https://ourcodeworld.com/articles/read/2412/what-is-zoneidentifier-windows-meaning-purpose-and-how-to-remove-it-safely).

The webpage states that <ins>"Zone.Identifier" is a hidden metadata file (technically called Alternate Data Stream or ADS) that Windows automatically attaches to files downloaded from the internet or received from external sources such as email attachments or network drives.</ins> It does not show up in Windows File Explorer. This hidden file contains crucial information like the origin or the security zone of the file. The purpose is to allow Windows and security applications to enforce policies based on where a file came from — for example, blocking the execution of files downloaded from untrusted sources.

We can use PowerShell to find out whether a file has a Zone.Identifier attached.

```powershell
Get-Item -Path "C:\Temp\Software Update\update\new_update.software" -Stream *
```

It will show the following output.

```txt
PSPath        : Microsoft.PowerShell.Core\FileSystem::C:\Temp\Software Update\update\new_update.software::$DATA
PSParentPath  : Microsoft.PowerShell.Core\FileSystem::C:\Temp\Software Update\update
PSChildName   : new_update.software::$DATA
PSDrive       : C
PSProvider    : Microsoft.PowerShell.Core\FileSystem
PSIsContainer : False
FileName      : C:\Temp\Software Update\update\new_update.software
Stream        : :$DATA
Length        : 123456

PSPath        : Microsoft.PowerShell.Core\FileSystem::C:\Temp\Software Update\update\new_update.software:Zone.Identifier
PSParentPath  : Microsoft.PowerShell.Core\FileSystem::C:\Temp\Software Update\update
PSChildName   : new_update.software:Zone.Identifier
PSDrive       : C
PSProvider    : Microsoft.PowerShell.Core\FileSystem
PSIsContainer : False
FileName      : C:\Temp\Software Update\update\new_update.software
Stream        : Zone.Identifier
Length        : 25
```

The first entry is the file as it appears in File Explorer. The second entry with `:Zone.Identifier` is the hidden metadata stream. When the Kiosk machine's security application detected this stream, it strongly suggests the application rejected the file because it assumed the file originated from an untrusted source. This is a common security measure to prevent potentially malicious files from being copied or executed.

## The Fix

The breakthrough gave us the answer. Downloading the file directly from the monitoring server to the Kiosk machine did not attach a Zone.Identifier, which is why the update succeeded. The original workflow — downloading the file to a computer first, then copying it to the USB — had already attached the Zone.Identifier during the initial download. The USB simply carried the file with the Zone.Identifier already present.

To fix the issue for future updates, we used PowerShell to remove the Zone.Identifier stream from the file after copying it from the USB:

```powershell
Remove-Item -Path "C:\Temp\Software Update\update\new_update.software" -Stream Zone.Identifier
```

This removes the hidden Zone.Identifier metadata. The Kiosk machine's security application no longer sees the file as originating from an untrusted source, and allows it to be copied to the target folder.

As a general practice, you can also use PowerShell to remove Zone.Identifier from any file downloaded from the internet:

```powershell
Unblock-File -Path "C:\path\to\file"
```

This uses the `Unblock-File` cmdlet, which is a simpler way to remove the Zone.Identifier stream without having to specify it explicitly.
