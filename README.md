# HelloRestSoft

A Bruno-like REST client built using `git-cola` libraries and `httpx`.

## Features
- Async HTTP requests using `httpx`
- Collection management (JSON based)
- Tabbed interface
- Request/Response viewing

## Installation

```bash
pip install -e .
pip install PyQt5  # or PySide2/6
```

## Running

```bash
hellorestsoft
```

## Development

The project structure reuses `git-cola`'s `cola` package for Qt utilities and widgets.
The main logic is in `hellorestsoft/`.
