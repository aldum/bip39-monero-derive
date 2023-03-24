### Dev setup

#### prerequisites

##### Arch-based

`python python-poetry`

##### Debian-based

`python3 python3-venv libpython<ver>-dev`

Substitute your python version, 3.9 or newer should be fine.
The packaged version of poetry is too old, so it needs to be installed via pip.

```shell
python -m venv .venv
source .venv/bin/activate
pip install poetry # for debian-based systems
poetry install
```
