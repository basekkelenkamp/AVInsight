# AVInsight

## Install project (windows)
1. Install python3.8 `https://github.com/adang1345/PythonWindows/raw/master/3.8.16/python-3.8.16-amd64-full.exe` Make sure to check the "Add Python 3.8 to PATH" checkbox
2. python --version (it should say 3.8.16)
3. Install poetry: `curl -sSL https://install.python-poetry.org | python -`
4. Add poetry path to environment
4. from AVInsight dir, run `poetry install`

## Create executable (not working yet)
1. poetry export --without-hashes --format=requirements.txt > requirements.txt
2. poetry run pyinstaller --onefile --add-data "static;static" --add-data "templates;templates" app.py
3. poetry run pyinstaller app.spec
