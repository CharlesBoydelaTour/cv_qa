# Readme

Hey there this is the start of the general readme.

## Getting started

This project relies on poetry as dependency management.

Initialize your virtual environment using `poetry install`

To add other python dependencies, use `poetry add <my-package`.

## Run the code

### Setup

The recommended way to run the code of this project is via CLI

## Documentation

The documentation process relies on mkdocs which allows to write markdown styled documentation.

Most of the documentation of the code is auto generated based on the docstring of the functions. Check the vscode extension `njpwerner.autodocstring` for automated docstring formatting.

You add other documentation pages by simply adding a new markdown file in the _docs_ folder.

To see your documentation in a local environment, use `mkdocs serve`.

### Personalization

To adapt the doc style to your style guidelines, change 
1. the colors in the `docs/stylesheets/extra.css` file
2. the logo and favicon in the `docs/assets/images/` folder


## Conventions

This project is based on a cookie cutter created by Capgemini Invent.

### Project tree

The project follows the tree structure described bellow :
```
the_project/
┣ data/ --> for all datafiles during development
┃ ┣ interim/ --> store intermediate data files
┃ ┣ processed/ --> store processed data files
┃ ┗ raw/ --> store raw data files that should never be modified
┣ docs/ -> stores mkdocs documentation
┣ models/ -> store all your models here
┃ ┗ dev_model.h5 -> dummy model file
┣ notebooks/ --> keep here all your exploratory notebooks
┣ tests/ --> for all your test files
┃ ┣ the_project/
┃ ┃ ┣ test_cli.py
┃ ┃ ┗ __init__.py
┃ ┣ test_config.py
┃ ┗ __init__.py
┣ the_project/ --> where the meat actually is
┃ ┣ data/ --> handles data transformation logic
┃ ┃ ┣ main.py
┃ ┃ ┗ __init__.py
┃ ┣ model/ --> handles modeling logic
┃ ┃ ┣ main.py
┃ ┃ ┗ __init__.py
┃ ┣ config.py --> pydantic-based configuration file
┃ ┣ log_conf.ini
┃ ┣ main.py --> main entry point
┃ ┗ __init__.py
┣ .gitignore
┣ INSTALL.md
┣ mkdocs.yml
┣ pyproject.toml -> poetry packaging configuration file
┗ README.md
```

### Naming

- In command line interfaces, all cli names and keyword arguments words are separated by "-"
- In python package, all modules words are separated by underscores.

For example:

```this-is-my-cli train --data-source /etc/config.yaml```

And handling python imports you would have:

```
from this_is_my_cli.model.main import train
```

Please note also that using Typer, function arguments such as "my_argument" are
automatically converted to "--my-argument" in the cli interface.