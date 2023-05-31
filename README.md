# AVInsight

## Technical explanation
The server starts a thread loop that takes care of:
1. Gathering PC metrics.
2. Writing metrics to the DB.
3. Streaming metrics to a socket, connected to the frontend.

When the config is updated, the server terminated the current thread, and starts a new thread with the updated configuration.

### Activity diagram
![Activity Diagram server   client AVInsight cropped](https://github.com/basekkelenkamp/AVInsight/assets/57452503/23e24059-bfc0-4409-9cf7-872e08545412)

## Start the application from executable (powershell)
`.\app.exe "C:\path\to\rootfolder\AVInsight"`

For me it is: `.\app.exe "F:\school\jaar4\the lighthouse internship\AVInsight"`

## Start from python environment (poetry)
`poetry run flask run`

## Development
### Create executable with Nuitka
`poetry run python -m nuitka --onefile --standalone app.py`

### Install poetry environment (manual way)
1. Install python3.8 `https://github.com/adang1345/PythonWindows/raw/master/3.8.16/python-3.8.16-amd64-full.exe` Make sure to check the "Add Python 3.8 to PATH" checkbox
2. python --version (it should say 3.8.16)
3. Open powershell, install poetry: `(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -`
4. Add poetry path to environment: open environment variables, to $PATH variable add: `%APPDATA%\Python\Scripts`
4. from AVInsight dir, run `poetry install`
