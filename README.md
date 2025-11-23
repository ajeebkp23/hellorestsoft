# HelloRestSoft

A Bruno-like REST client built using `git-cola` libraries and `httpx`.

## Features
- Async HTTP requests using `httpx`
- Collection management (JSON based)
- Tabbed interface
- Request/Response viewing

## Installation

First, fetch the `git-cola` dependency:

```bash
git clone --depth 1 https://github.com/git-cola/git-cola.git
```

> **Note:** This project is currently tested against `git-cola` commit `a810c8e`.

Then set up the environment:

```bash
# venv
python -m venv venv
. venv/bin/activate
# or
source venv/bin/activate

pip install -e .
#pip install PyQt5  # or PySide2/6
pip install PySide6
```

## Running

```bash
# venv
venv/bin/hellorestsoft
```

## Development

The project structure reuses `git-cola`'s `cola` package for Qt utilities and widgets.
The main logic is in `hellorestsoft/`.
