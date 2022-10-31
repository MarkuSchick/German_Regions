# GermanRegions

# venv

https://towardsdatascience.com/8-must-know-venv-commands-for-data-scientists-and-engineers-dd81fbac0b38

1. Create a virtual environment

`python3 -m venv my_venv`

2. Activate a virtual environment

`source my_venv/bin/activate`

3. Deactivate a virtual environment

`deactivate`

4. Remove/Delete a virtual environment

`rm -rf /path/to/my_venv`

5. Clear an existing virtual environment (deletes all packages installed in the virtual environment)

`python3 -m venv --clear path/to/my_venv`

6. Update Python version

`python3 -m venv /path/to/my_venv --upgrade`

7. Give virtual environment access to system site-packages

`python3 -m venv /path/to/my_venv --system-site-packages`

8. Find help

`python3 -m venv -h`

# Install the environment:

Type

`conda env create -f environment.yml`

to create the environment from the file.
