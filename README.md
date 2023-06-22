# AVInsight
This app is meant for monitoring PC metrics in an environment for immersive installations. This app was built as my thesis project for The Lighthouse of Digital art in Berlin.

[WATCH DEMO](https://www.youtube.com/watch?v=msCJtoHTKJM)

# HOW TO INSTALL

1. Download the [latest release](https://github.com/basekkelenkamp/AVInsight/releases) from github.
2. Extract the zip, and place all files in a folder where you want to install AVInsight.

### For the Lighthouse servers:
1. Download the zip as explained above, and replace the files in `Program Files (x86)\AVInsight` with the new files.
2. If you want to keep your data, you should keep your old database file which can be found in: database/AVInsight.db.

# Technical explanation
The server starts a thread loop that takes care of:
1. Gathering PC metrics.
2. Writing metrics to the DB.
3. Streaming metrics to a socket, connected to the frontend.

When the config is updated, the server terminated the current thread, and starts a new thread with the updated configuration.

### Note
The raw archive data is still available under `archive/raw`, but it is not recommended to go there while the show is running, as it can cause big lags. 

### Activity diagram
![Activity Diagram server   client AVInsight cropped](https://github.com/basekkelenkamp/AVInsight/assets/57452503/23e24059-bfc0-4409-9cf7-872e08545412)

## Start the application from executable (powershell)
1. Open powershell as admin and browse to the AVInsight directory: `Set-Location 'C:\path\to\rootfolder\AVInsight\'`
2. Start the app with the command: `.\app.exe "C:\path\to\rootfolder\AVInsight"`

(For me it is: `.\app.exe "F:\school\jaar4\the lighthouse internship\AVInsight"`)

# Development
This repository is split into different sections. `app.py` holds all the logic for flask routes, sockets and threads. `database/db.py` holds all functions relevant to the database. The `config/` folder holds the `config.json` file that can be edited by hand, but it is recommended to do it via the AVInsight UI, which uses functions in the `load_config.py`.

## poetry
Poetry is a versatile package manager en virtual environment for python. All dependencies are defined in `pyproject.toml`.

### Install poetry environment
1. Install python3.8 `https://github.com/adang1345/PythonWindows/raw/master/3.8.16/python-3.8.16-amd64-full.exe` Make sure to check the "Add Python 3.8 to PATH" checkbox
2. python --version (it should say 3.8.16)
3. Open powershell, install poetry: `(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -`
4. Add poetry path to environment: open environment variables, to $PATH variable add: `%APPDATA%\Python\Scripts`
4. from AVInsight dir, run `poetry install`

### Start app from poetry
`poetry run flask run`

### Run tests
`poetry run pytest`

## Standalone executable
The standalone executable allows you to easily deploy AVInsight on any windows 10 machine without having to install python or other dependencies. Simply download all the files from the github repository.

### Create executable with Nuitka
Remove pytest dependency: `poetry remove pytest` (remember to add it back later if needed with `poetry add pytest`)

Create executable: `poetry run python -m nuitka --onefile --standalone app.py`
