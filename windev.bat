
if exist "scratch\venv-geoiq" goto cont

C:\Python25\Scripts\virtualenv.exe "scratch\venv-geoiq"
scratch\venv-geoiq\Scripts\python.exe setup.py
scratch\venv-geoiq\Scripts\easy_install.exe ipython

:cont

scratch\venv-geoiq\Scripts\activate.bat