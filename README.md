# AVInsight

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
