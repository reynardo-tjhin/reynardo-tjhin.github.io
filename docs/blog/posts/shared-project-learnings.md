---
title: Shared Project Learnings
slug: shared-project-learnings
date: 2026-07-24
categories:
  - Software Development
description: Some of the learnings from working in a project with my friend
comments: true
---

# Shared Project Learnings

My friend and I have been working on a website for golfers to input and track their scores on a leaderboard, competing against their friends. We use FastAPI as our backend and PostgreSQL as the primary database. In this blog, I am writing notes and lessons I have taken as we develop the app.

<!-- more -->

## Source Control

When starting a new feature in a shared project, it is ideal to create a new branch and work on that branch instead of the main branch. This is to prevent conflicts during development. The typical workflow usually goes like this:

```sh
git checkout dev
git pull origin dev # make sure your local dev is up to date first!
git checkout -b feature/feature-A # branch off dev
git push -u origin feature/feature-A # first push, sets upstream tracking
```

Once the feature `feature/feature-A` is completed, you can either:

1. Open a pull request and merge `feature/feature-A` to the `dev` branch. OR
2. Merge locally and then push to the repository.

    ```sh
    git checkout dev
    git pull origin dev # get the latest dev
    git merge feature/feature-A # merge feature/feature-A to dev branch
    git push # push to the repository
    ```

Branch names are equally important. Use **hyphens** rather than underscores. Here is how to name the branch according to the work.

1. For new functionality or new features, name the branch `feature/<feature-name>`
2. For fixing bugs in the code, name the branch `bugfix/<bugfix-name>`
3. For urgent production patches, name the branch `hotfix/<hotfix-name>`
4. For preparing new releases, name the branch `release/<release-version>`
5. For refactoring the code, name the branch `refactor/<feature-name>`
6. For updating/writing documentation, name the branch `docs/<feature-name>`

## Forgot `postgres` User Password? Here's the Fix.

I had a problem trying to sign in as the `postgres` user. I tried different passwords but all of them failed. I had to reset the password and here is what I did.

1. Locate the `pg_hba.conf` file: `C:\Program Files\PostgreSQL\18\data\pg_hba.conf`.
    It is usually located in the installed folder of PostgreSQL.
2. Temporarily edit `pg_hba.conf` to allow trust authentication.
    In the line for host connections on 127.0.0.1/32, remove the word `scram-sha-256` and change it to `trust`. For e.g.
    ```txt
    host    all             all             127.0.0.1/32            scram-sha-256
    ```
    to 
    ```txt
    host    all             all             127.0.0.1/32            trust
    ```
3. Restart the PostgreSQL service in Windows: open `services`, look for `postgresql-x64-18 - PostgreSQL Server 18` and restart the `PostgreSQL` service.
4. Open pgAdmin4 or psql and run the following command: 
    ```sql
    ALTER USER postgres WITH PASSWORD 'new_password';
    ```
5. Restart pgAdmin4 or psql and log in using the new password. It should work. Close the applications.
6. Edit `pg_hba.conf` back to the original.
    From
    ```txt
    host    all             all             127.0.0.1/32            trust
    ```
    to
    ```txt
    host    all             all             127.0.0.1/32            scram-sha-256
    ```
7. Restart the PostgreSQL service, similar to step 3.

## Software Development Tips

The first not-so-obvious mistake when I was developing the FastAPI backend was writing everything in the router layer (database queries, business logic, etc.). That is not the ideal way as it increases the difficulty to test the code. It is fine for small projects, but it is better to separate them into different layers. Here is what I initially did:

```txt
backend/
├─ app/
│  ├ core/
│  │  ├ __init__.py
│  │  ├ config.py
│  │  └ database.py    # init database engine and session
│  ├ models/
│  │  ├ __init__.py
│  │  ├ base.py
│  │  └ courses.py     # the SQLAlchemy model
│  ├ routers/
│  │  ├ __init__.py
│  │  └ course.py      # the FastAPI router
│  ├ schemas/
│  │  ├ __init__.py
│  │  └ course.py      # the Pydantic model
│  ├ __init__.py
│  ├ main.py
├─ tests/
│  ├ __init__.py
│  ├ conftest.py
│  └ test_golf_course.py
```

The business logic and the database queries all end up in a single `course.py` in the `routers` folder. The general advice with HTTP routers is that they need to be as lightweight as possible. The routers usually just return whatever the service layer is providing. The service layer should only handle the business logic. Therefore, this also requires a database (or a client) layer to fetch the data. Below is a more ideal version.

```txt
backend/
├─ app/
│  ├ core/
│  │  ├ __init__.py
│  │  ├ config.py
│  │  └ database.py    # init database engine and session
│  ├ models/           # define the SQLAlchemy models
│  │  ├ __init__.py
│  │  ├ base.py
│  │  └ courses.py
│  ├ clients/          # the client layer - fetches data
│  │  ├ __init__.py
│  │  └ course.py
│  ├ schemas/          # define the Pydantic models - type checking
│  │  ├ __init__.py
│  │  └ course.py
│  ├ services/         # the service layer - business logic
│  │  ├ __init__.py
│  │  └ course.py
│  ├ routers/          # the FastAPI HTTP router
│  │  ├ __init__.py
│  │  └ course.py
│  ├ __init__.py
│  ├ main.py
├─ tests/
│  ├ __init__.py
│  ├ conftest.py
│  └ test_golf_course.py
```
