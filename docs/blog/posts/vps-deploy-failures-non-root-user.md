---
title: Five CI/CD Failures Deploying to a VPS as a Non-Root User
slug: vps-deploy-failures-non-root-user
date: 2026-10-22
categories:
  - DevOps
description: A GitHub Actions deploy to a VPS that broke one step at a time when the pipeline moved from root to a dedicated deploy user — and how each failure was diagnosed and fixed.
comments: true
---

# Five CI/CD Failures Deploying to a VPS as a Non-Root User

A GitHub Actions deploy to a VPS that broke one step at a time when the pipeline moved from root to a dedicated deploy user — and how each failure was diagnosed and fixed:

* `git pull` failing with the error "Host key verification failed" (no `known_hosts`, no deploy key)
* `git remote get-url origin` still pointing at a fork
* `systemctl restart` demanding the root password because the sudoers rule was never invoked
* a `package-lock.json` accidentally gitignored, and
* a `.venv` whose `bin/python` symlink pointed into `/root`.

This blog post also contains the original `deploy.yml` file that has the above issues, and the `golftracker.service` for readers in the future who might need an example of a `.service` file.

<!-- more -->

## Deploy YAML code

Below is the initial code for the problematic CI/CD workflow (`deploy.yml`).

```yaml linenums="1"
name: Balling.au CI/CD Pipeline

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Deploy to Production
        uses: appleboy/ssh-action@v1.2.0
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script_stop: true
          script: |
            cd /var/www/golf-score-tracker
            
            echo "--- Pulling latest code ---"
            git pull origin main
            echo "--- Syncing Python dependencies & running migrations ---"
            /home/deploy/.local/bin/uv sync
            PYTHONPATH=/var/www/golf-score-tracker/backend /home/deploy/.local/bin/uv run alembic upgrade head
            
            echo "--- Building Frontend ---"
            cd frontend
            # Use sed to safely replace or append the VITE_API_URL without wiping .env
            if grep -q "^VITE_API_URL=" .env; then
              sed -i 's|^VITE_API_URL=.*|VITE_API_URL=${{ secrets.VITE_API_URL }}|' .env
            else
              echo "VITE_API_URL=${{ secrets.VITE_API_URL }}" >> .env
            fi
            npm install
            npm run build
            
            echo "--- Restarting Service ---"
            cd ..
            systemctl restart golftracker
            echo "Deployment completed successfully."
```

## Issue #1: Host Key Verification Failed

### Problem

When transitioning the CI/CD workflow from the `root` user to a dedicated `deploy` user, I encountered the following error during the `git pull` step:

```txt
YYYY-MM-DDTHH:MM:SS.SSSSSSSZ --- Pulling latest code ---
YYYY-MM-DDTHH:MM:SS.SSSSSSSZ Host key verification failed.
YYYY-MM-DDTHH:MM:SS.SSSSSSSZ fatal: Could not read from remote repository.
YYYY-MM-DDTHH:MM:SS.SSSSSSSZ Please make sure you have the correct access rights
YYYY-MM-DDTHH:MM:SS.SSSSSSSZ and the repository exists.
YYYY-MM-DDTHH:MM:SS.SSSSSSSZ 2026/09/22 14:29:19 Process exited with status 1
YYYY-MM-DDTHH:MM:SS.SSSSSSSZ ##[error]Process completed with exit code 1.
```

This error message is from line 23 `git pull origin main`.

### Why It Happened

When the `git pull` command was executed, the SSH client attempted to verify the server's identity. Because this is an automated CI/CD workflow, there was no human available to respond to the interactive prompt: *"Are you sure you want to continue connecting?"*. `ssh` aborted and presented the error: `Host key verification failed`.

The fundamental issue is that the `deploy` user had not completed the two-way authentication required for secure communication.

* `/home/deploy/.ssh/known_hosts` was missing (No **Host Trust**).
* `/home/deploy/.ssh/id_ed25519` and its public counterpart (`.pub`) were missing (No **User Authentication**).

*Note: While `/home/deploy/.ssh/authorized_keys` existed, it only allowed GitHub to SSH **into** the VPS. It did not help the VPS talk **to** GitHub.*

To understand why the fix required both `ssh-keyscan` and a new keypair, we can look at the SSH handshake between the **Client (VPS)** and the **Server (GitHub)**:

1.  **TCP Connection**: A connection is established.
2.  **Server Identity Check (Host Trust)**: The server presents its host key. The client (the VPS) checks its `known_hosts` file to see if it **recognises** the server. **(This is where the failure occurred)**.
3.  **Client Identity Check (User Authentication)**: The server (GitHub) checks its `authorized_keys` (or Deploy Keys) to see if the user is **authorised**. For this to work, GitHub uses the VPS' public key to verify the signature, proving the VPS owns the private key. Nothing is encrypted to the client key.
4.  **Encrypted Session**: A secure session is established, and the `git` command is executed. When the `git pull origin main` command is executed, data is encrypted under the symmetric session key from the key exchange (Diffie‑Hellman). The host key authenticates the server; the client key authenticates the client. Neither one carries the payload.

The `authorized_keys` file and the `known_hosts` file belong to different "directions".

1. Inbound: GitHub $\rightarrow$ VPS (The "Guest List")

    When your GitHub Action runs, the Runner is the Client and your VPS is the Server.
    
    - The Goal: The VPS needs to know the Runner is allowed to enter.
    - The Tool: The VPS uses `authorized_keys` as a Guest List. If the Runner's key is on that list, the VPS lets them in.
    - This is why your Runner could SSH into the VPS successfully.

2. Outbound: VPS $\rightarrow$ GitHub (The "Contact List")

    When your git pull command runs, your VPS is now the Client and GitHub is the Server.
    
    - The Goal: The VPS needs to know it is actually talking to the real GitHub and not a malicious imposter (a Man-in-the-Middle attack).
    - The Tool: The VPS uses `known_hosts` as a Contact List. It looks up GitHub's "fingerprint" in that file to ensure the server is legitimate.
    - This is where you failed: the VPS had no "Contact List" for GitHub, so it couldn't "recognise" it.

Below is the SSH file reference guide.

| File | Purpose | Direction |
| :--- | :--- | :--- |
| `authorized_keys` | Lists clients/servers **authorised** to log in. | **Inbound** (e.g., GitHub $\rightarrow$ VPS) |
| `known_hosts` | Stores identities of trusted servers. | **Outbound** (e.g., VPS $\rightarrow$ GitHub) |
| `id_ed25519` | The private key used to prove identity. | **Outbound** (e.g., VPS $\rightarrow$ GitHub) |
| `id_ed25519.pub` | The public key shared with the server. | **Outbound** (e.g., VPS $\rightarrow$ GitHub) |

### The Solution

1. Log in as deploy user: `ssh deploy@[ip-address]`
2. Confirm the user: `whoami`
3. Generate a fresh key-pair value: `ssh-keygen -t ed25519`
    * The system will prompt for a file path to save the key:
      ```
      Generating public/private ed25519 key pair.
      Enter file in which to save the key (/home/deploy/.ssh/id_ed25519):
      ```
      Press `Enter` to save the key pair in the default location.
    * Next, it will prompt for a passphrase:
      ```
      Enter passphrase (empty for no passphrase):
      ```
      Press `Enter` to use an empty passphrase (required for unattended CI/CD).
    * It will prompt you to confirm the empty passphrase:
      ```
      Enter same passphrase again:
      ```
      Press `Enter` again.
    * The output will display the results:
      ```
      Your identification has been saved in /home/deploy/.ssh/id_ed25519
      Your public key has been saved in /home/deploy/.ssh/id_ed25519.pub
      The key fingerprint is:
      SHA256:...
      The key's randomart image is:
      +--[ED25519 256]--+
      | ...             |
      | ...             |
      +----[SHA256]-----+
      ```
4. Ensure correct permissions
    * `chmod 700 /home/deploy/.ssh`
    * `chmod 600 /home/deploy/.ssh/id_ed25519`
    * `chmod 644 /home/deploy/.ssh/id_ed25519.pub`
    
    !!! info

        Note: Understanding Permissions

        * `chmod 700`: Owner has Read, Write, and Execute permissions (7 = 4+2+1); Group and Others have none.
        * `chmod 600`: Owner has Read and Write permissions (6 = 4+2); Group and Others have none.
        * `chmod 644`: Owner has Read and Write; Group and Others have Read-only access.

5. Retrieve the public key: `cat /home/deploy/.ssh/id_ed25519.pub`
    * The `.pub` file contains your public key.
    * Example content: `ssh-ed25519 AAAA... deploy@Balling`

6. Register the key on GitHub:
    * Go to `Repository > Settings > Deploy keys > Add deploy key`.
    * Title: `deploy@Balling`
    * Key: Paste the content from step 5.
    * Allow write access: Leave this **unchecked** (the production server only needs to pull code, not push).

7. Trust the GitHub host:
    * Run the following commands
    ```bash
    ssh-keyscan -t ed25519 github.com >> ~/.ssh/known_hosts
    chmod 600 ~/.ssh/known_hosts
    cat ~/.ssh/known_hosts
    ```
    * Security Tip: Verify that the fingerprint in your known_hosts matches the official fingerprints listed in the [GitHub Documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints).

8. Verify: `ssh -T git@github.com`
    * You should see a greeting message from GitHub (e.g., "Hi username/repository! You've successfully authenticated...").


## Issue #2: `origin` Pointing at a Fork

### Problem

During the deployment process, I discovered that the local repository on the VPS was tracking the wrong remote. Running `git remote -v` revealed that the `origin` was pointing to a fork rather than my own canonical repository.

```bash
origin  git@github.com:Collaborator/repository.git (fetch)
origin  git@github.com:Collaborator/repository.git (push)
```

This meant that any new code pushed to my repository (reynardo-tjhin/repository) would not be picked up by the CI/CD pipeline, as the server was still pulling from the fork.

### Why It Happened

This was a configuration oversight during the initial setup. A collaborator had been tasked with setting up the CI/CD workflow and, to test the process safely, had performed the initial configuration using their own fork of the project. Consequently, the VPS was configured to track the fork instead of the primary repository.

### The Solution

The fix involved repointing the origin remote to my repository and verifying that the connection was correctly established.

1. Repoint the Remote URL

    I updated the remote URL to point to the correct repository. It is important to use the SSH format (git@github.com:...) rather than HTTPS, as the deploy user relies on SSH Deploy Keys for authentication.

    `git remote set-url origin git@github.com:reynardo-tjhin/repository.git`

2. Verify the Change
    
    I confirmed the update by checking the remote configuration again: `git remote -v`
    Expected output:
    ```bash
    origin  git@github.com:reynardo-tjhin/repository.git (fetch)
    origin  git@github.com:reynardo-tjhin/repository.git (push)
    ```

3. Ensure a Clean Transition (Best Practice)

    Before running the first deployment, I performed a "dry-run" fetch to ensure there were no divergence issues between the fork and the main repository:

    ```txt
    # Fetch the latest state from the new origin
    git fetch origin

    # Check the status to ensure a clean fast-forward is possible
    git status -sb
    ```

    *Note: If the repositories had diverged, I would have needed to perform a git reset --hard origin/main to align the VPS strictly with the canonical repository.*


## Issue #3: `systemctl restart` Asks for the Root Password

### Problem

Line 41 `systemctl restart golftracker` stops the CI/CD script and causes a new issue: `"Authentication is required to restart 'golftracker.service' Authenticating as: root Password: "`.

### Why It Happened

There are two doors to a privileged `systemctl` verb, and only one of them had been
configured on this VPS:

* **polkit/systemd** — for a remote SSH session, its default is to demand the `root`
  password. That is why the prompt read `Authenticating as: root` and not
  `[sudo] password for deploy`.
* **sudo** — requires a matching rule in sudoers, and is consulted *only* when you
  actually type `sudo`.

Why polkit is involved at all: a system unit belongs to the system manager (PID 1), and `systemctl` does not act on files — it sends a D-Bus message to PID 1 saying "restart this unit". PID 1 then asks polkit whether the caller may manage system units, and for a remote SSH session the answer defaults to "only with admin authentication". That gate sits in front of the unit, so it applies whatever the unit's own `User=` says.

When my collaborator moved the pipeline from `root` to a dedicated `deploy` user, he had already gone through the second door and added the rule for it:

```
$ sudo -l -U deploy
User deploy may run the following commands on Balling:
    (ALL) NOPASSWD: /bin/systemctl restart golftracker
```

So `deploy` *was* allowed to restart the service. The step still failed because line 41 ran bare `systemctl restart golftracker` — no `sudo`, so sudoers was never read. The command fell through to polkit instead, polkit asked for the `root` password, and in CI there is nobody to type it. The permission existed; the workflow simply never asked for it.

For reference, an unprivileged user can run read-only verbs such as `systemctl status golftracker` or `systemctl list-units` without any privilege. `restart` on a system unit — and this one runs as `User=root` (line 6 of the unit file below) — is always refused with `Permission denied` / `Authentication required` / `must be root`.

The below shows the content of `/etc/systemd/system/golftracker.service`.

```ini linenums="1"
[Unit]
Description=Golf Score Tracker API
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/golf-score-tracker
Environment="PYTHONPATH=/var/www/golf-score-tracker/backend"
EnvironmentFile=/var/www/golf-score-tracker/.env
ExecStart=/var/www/golf-score-tracker/.venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

!!! info

    `User=root` describes which account the *process* runs as once systemd has started it. It has no bearing on who may restart the unit — that decision is made before systemd looks at the setting.

### The Solution

> Tip: run `sudo -iu deploy` to become the `deploy` user.

1. SSH into the VPS as the `root` user.
2. Check the user `deploy`'s permission.

    * run `sudo -l -U deploy`. 
    * if the `(ALL) NOPASSWD: /bin/systemctl restart golftracker` line is already
      present, skip to step 5 — the server was already authorised and only the workflow
      was wrong.
    * if instead it ends with `User deploy is not allowed to run sudo on Balling`,
      continue to step 3.

3. Grant the deploy user permission to run this one command without a password.

    * as the root user, create a file `deploy` in `/etc/sudoers.d`:
      `sudo EDITOR=nano visudo -f /etc/sudoers.d/deploy`
    * write the following content to the file:
      `deploy ALL=(ALL) NOPASSWD: /bin/systemctl restart golftracker`
    * save the file: `CTRL + X` > `y` > `ENTER`

    !!! info

        `visudo` edits the file the same way `nano` does, but refuses to save if the syntax does not parse and restores mode `440`. A sudoers error that `nano` would happily save breaks `sudo` for every account on the machine. Note also that drop-in filenames may not contain a `.` — `deploy.bak` in that directory is silently ignored.

4. Check the user `deploy`'s permission again.

    * run `sudo -l -U deploy`: we should see the following.
      ```
      Matching Defaults entries for deploy on Balling:
          env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty

      User deploy may run the following commands on Balling:
          (ALL) NOPASSWD: /bin/systemctl restart golftracker
      ```
    * run `sudo -iu deploy` to become the `deploy` user — sudoers does not apply to
      `root`, so the command has to be run as `deploy` to prove the rule works
    * run `sudo -n /bin/systemctl restart golftracker; echo $?`: we should see `0`
    * run `exit` to leave the `deploy` user

5. In the `deploy.yml` file, change `systemctl restart golftracker` to
   `sudo -n /bin/systemctl restart golftracker`. `-n` matters for CI: non-interactive —
   fail fast instead of hanging on `[sudo] password for deploy:` prompt that nobody can
   answer in Actions.

!!! info

    sudoers matches the command **literally**. `sudo -n /bin/systemctl restart golftracker.service` fails with `sudo: a password is required` even though systemd accepts both spellings, because `golftracker` and `golftracker.service` are different strings. Keep the rule and the workflow character-for-character identical.


## Issue #4: Missing `package-lock.json` for npm

### Problem

While tidying the project, I accidentally added `package-lock.json` to `.gitignore` — the kind of small mistake that is easy to make and easy to miss. On its own, nothing breaks, but it hurts as soon as you work with more developers or deploy to a server: without the lockfile, `npm install` can resolve different dependency versions on each machine. If those resolutions land on different major versions of a library, the code that works on one machine may not work on another — including the production server. This issue would never have happened if the lockfile had simply stayed tracked.

### The Solution

All commands below run inside `frontend/` unless stated otherwise: the lockfile always sits next to the `package.json` it describes, so the file this issue is about is `frontend/package-lock.json`.

1. Remove the `package-lock.json` entry from `.gitignore` (the lockfile itself should be tracked). Check both the root `.gitignore` and `frontend/.gitignore` — the rule can hide in either.
2. Get the latest working `package-lock.json` (I took it from my collaborator's commit since he was the one that initialised the packages for the frontend.)
3. Run `npm ci` (not `npm install`)
    - `npm install` is only run once to install the packages and generate the `package-lock.json`.
    - Because I recovered the lockfile from an older commit, `npm ci` doubles as a check: it only succeeds if `package-lock.json` and `package.json` are still in sync. If they had drifted apart, it fails right here, on my machine, instead of silently breaking the production deploy.
4. Update the `deploy.yml` (don't run both `npm install` and `npm ci`; change `npm install` to `npm ci`).
5. Commit the `package-lock.json` and `deploy.yml` to the repository.

!!! info

    Why running both `npm install` and `npm ci` is incorrect:

    * `npm install` re-resolves the caret (`^`) ranges in `package.json` on every run and can rewrite `package-lock.json` on the server — and that modified lockfile is never committed back, so the server quietly drifts away from everyone else's versions.
    * Running `npm ci` immediately after deletes `node_modules/` and reinstalls everything from the lockfile anyway — so the preceding `npm install` only costs time and reintroduces non-determinism for zero benefit. Replace the `npm install` step with `npm ci`; don't append.
    * Also note that `npm ci` cannot work without a lockfile: if `package-lock.json` is not committed, it fails on the VPS with a "missing lockfile" error. That is why both changes must ship together — the lockfile committed, and the workflow switched to `npm ci` only.


## Issue #5: `uv sync` Permission Error

### Problem

With the `deploy` user finally able to run the workflow, the next step produced a new error. The failing line was `/home/deploy/.local/bin/uv sync`:

```txt
YYYY-MM-DDTHH:MM:SS.SSSSSSSZ error: Failed to query Python interpreter
YYYY-MM-DDTHH:MM:SS.SSSSSSSZ   cause: failed to canonicalize path `/var/www/golf-score-tracker/.venv/bin/python`: Permission denied (os error 13)
```

At first glance this looks like deploy cannot read the virtual environment — but deploy owned the .venv and could read every file in it. So what was blocked?

### Why It Happened

This was the last leftover from the root → deploy migration. A virtual environment does not contain its own Python interpreter - it symlinks `bin/python` to the real interpreter somewhere else. `uv` keeps its own Python installations under `~/.local/share/uv/python/`, and the `venv` had been built back when `uv sync` ran as `root`, where `~` is `/root`. So `.venv/bin/python` pointed at `/root/.local/share/uv/python/cpython-3.13-.../bin/python3.13`.

To find exactly where deploy got blocked, I walked the path with `namei -l`. It prints the permissions and owner of every component from `/` to the target, follows the final symlink, and walks the target's path too:

```bash
$ namei -l /var/www/golf-score-tracker/.venv/bin/python

# ... (components up to .venv/bin resolve fine) ...

lrwxrwxrwx deploy deploy python -> /root/.local/share/uv/python/cpython-3.13-linux-x86_64-gnu/bin/python3.13
drwxr-xr-x root root /
drwx------ root root root
                   .local - Permission denied
```

The last three lines are the whole diagnosis: `/root` is `drwx------` (700), so deploy cannot even enter it — let alone reach the interpreter inside. To "canonicalise" a path, `uv` must traverse every directory along it, which fails at `/root` with Permission denied (os error 13).

I checked the symlink itself first (command: `stat -c '%U %G %a' /var/www/golf-score-tracker/.venv/bin/python*`) and it showed `777` permissions — a red herring. Symlinks always show `rwxrwxrwx`, and Linux ignores symlink permissions entirely; access is decided by each directory traversed along the way. That is why a 777 link can still be unreachable: deploy was stopped at `/root`, before the link's target was ever reached.


### The Solution

!!! info
    
    Where does `uv` know the virtual environment is in `.venv`? Nowhere in the repo - I have no `[tool.uv]` section and no `uv.toml`. It is `uv`'s default convention: it walks up from the current directory to find `pyproject.toml`, then uses `<project-root>/.venv`. That is also why the sync command must run from the project root - run it from `frontend/` or `backend/` and `uv` would create a second venv somewhere else.

1. Confirm the diagnosis: `readlink /var/www/golf-score-tracker/.venv/bin/python`: if it prints a path under `/root/`, the venv is bound to root's interpreter.
2. Give deploy its own interpreter (as deploy): `uv python install 3.13` - the version pin comes from `.python-version` in the repository. This downloads CPython into `/home/deploy/.local/share/uv/python/...`. Doing this before deleting anything keeps the downtime window short: `uv sync` below then reuses the installed interpreter instead of downloading it mid-deploy.
3. Stop the service (as `root`): `systemctl stop golftracker`.
4. Delete the root-bound `.venv` folder (as root): `rm -rf /var/www/golf-score-tracker/.venv`. No backup is needed - `uv.lock` + `pyproject.toml` + `.python-version` fully determine the environment, so a fresh `uv sync` rebuilds it.
5. Recreate it as `deploy` from the project root: `cd /var/www/golf-score-tracker && uv sync` — builds a fresh `.venv` deploy-owned end-to-end, with `bin/python` pointing inside `/home/deploy/...`.
6. Bring everything back up: `uv run alembic upgrade head`, the frontend build (Issue #4's `npm ci`), then `sudo -n /bin/systemctl restart golftracker`. The first two are optional - the next CI run repeats them - but the restart is not: step 3 left the service stopped.

Verify:

* `readlink .venv/bin/python`: a `/home/deploy/...` path, no `/root` anywhere.
* `ls -ld` on the `.venv` shows `deploy` deploy ownership.
* `uv sync` runs clean - no "canonicalize ... Permission denied".

## Acknowledgements

The issues described here were diagnosed with help from Muse Spark with OpenCode as the harness, and this post was reviewed and enhanced by Gemma 4 26B A4B and ISTA-DASLab/Qwen3.8 Flash Next GSQ RCO.
