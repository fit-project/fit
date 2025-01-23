### 1. If already active virtualens deactive it just to execute deactive command
```
deactivate
```
### 2. Modify this code line in poetry poetry_plugin/post_install.py with local repository
custom_framework_path = Path("INSERT-FRAMEWORK-PATH")

### 3. Remove this comment from pyproject.toml
#[tool.poetry.scripts]
#post-install = "scripts.poetry_plugin:post_install"

### 4. Config poetry virtualenvs.path
```
poetry3.11 config virtualenvs.path .virtualenvs/fit
```
### 5. Intall packages
```
poetry3.11 install  
```
### 6. Activate local virtualenvs
```
source .virtualenvs/fit/fit-AiLXs-z0-py3.11/bin/activate
```
### 7. Run post install
```
poetry3.11 run post-install
```
### 8. Reset virtualenvs.path
```
poetry3.11 config --unset virtualenvs.path
```
### 9. Verify python path is correct
```
which python
/path/to/custom/.virtualenvs/fit/fit-AiLXs-z0-py3.11/bin/python
```
### 10. Launch fit
```
python fit.py
```
