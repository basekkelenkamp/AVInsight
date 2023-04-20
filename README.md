# AVInsight

## Create executable (windows)
1. run `install_dependencies.bat`
2. poetry run pyinstaller --onefile --add-data "static;static" --add-data "templates;templates" app.py
3. poetry run pyinstaller app.spec
