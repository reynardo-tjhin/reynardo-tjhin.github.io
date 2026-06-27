---
title: Setting Up PostgreSQL
slug: postgresql-setup
date: 2026-06-27
categories:
  - Software Development
description: Document setting up PostgreSQL on my local machine
comments: true
---

# Setting Up PostgreSQL on Windows 11

In this blog post, I am documenting the steps that I took to set up PostgreSQL on my local machine (Windows 11).

<!-- more -->

## The Steps I Took

1. Link: [Download PostgreSQL on Windows](https://www.postgresql.org/download/windows/)
2. Click on the link "**Download the installer** certified by EDB for all supported Postgres versions."
3. Install based on the OS (in my case: Windows 11)
4. Once the installation has completed, click on the installer
5. Below are the setup questions
    - Installation Directory: "C:\Program Files\PostgreSQL\18"
    - Additional Components to be installed:
        - PostgreSQL server
        - pgAdmin 4
        - Stack Builder
        - Command Line Tools
    - Data Directory: "C:\Program Files\PostgreSQL\18\data"
    - Provide password for the database superuser (postgres). 'postgres' is the superuser's username
    - Port: 5432
    - Locale (used by the new database cluster): DEFAULT
6. After the setup has completed, I **unchecked** the option to launch stack builder at exit
7. After clicking on the "Finish" button, PostgreSQL server started in the background.
    - To check: open Task Manager and search for postgre
    - There should be 1 background process: `PostgreSQL Server`
8. Installation Completed!

## The Additional Component - pgAdmin 4

Back when I was in university learning SQL, I was confused with the different applications I needed to download to run PostgreSQL. I will try to break down the purposes of different applications in this section.

Firstly, we have PostgreSQL server. This is the database server. It listens to incoming connections and accepts them. It runs the queries that users ask and return the output. The PostgreSQL server is the main component.

Then, we have pgAdmin 4 which is like a graphical user interface to the PostgreSQL server. Opening up pgAdmin 4 for the first time, you will see one server already installed - PostgreSQL 18 (which is the version that was installed). When pgAdmin 4 is first opened, it prompts for the 'postgres' user that was set during installation. Check the "Save Password" for the application to remember.

![pgAdmin 4 Dashboard](../../images/pgAdmin-4-dashboard.png)

There should be a default "postgres" database already created for the superuser "postgres". You can create a new database by selecting the "Databases" dropdown, right-click, click on "Create" and "Database...".

![pgAdmin 4 Create New Database](../../images/pgAdmin-4-create-new-database.png)

On the left-hand side, on the third row, there's a workspace button. The workspace is something like an SSH terminal to connect to a PostgreSQL database server instead of a normal server. Input the following to access the terminal and run SQL queries. Then, click on "Connect & Open PSQL".

```txt
Server Name: localhost
Host name/address: 127.0.0.1
Port: 5432
Database: the database
User: postgres
Password: [password]
```

![pgAdmin 4 Workspace](../../images/pgAdmin-4-workspace.png)

## Working with Python SQLAlchemy ORM

The following code shows a simple way of using SQLAlchemy ORM to connect to a PostgreSQL database. If it fails, it will show errors. Ensure that the database is already created.

```py
# pip install psycopg2 (or psycopg2-binary)
from sqlalchemy import create_engine

# this should be in .env (hardcoded for viewing purposes in this blog)
DATABASE_URL="postgresql+psycopg2://username:password@localhost:5432/db_name"

# create database engine
engine = create_engine(DATABASE_URL)

# connect to the PostgreSQL database
try:
    conn = engine.connect()
    print('Connected')

    # close the PostgreSQL database connection
    conn.close()
except Exception as e:
    print(f'Failed to connect: {e}')    
```
