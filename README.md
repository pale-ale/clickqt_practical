# Welcome to clickqt

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/dokempf/clickqt/ci.yml?branch=main)](https://github.com/dokempf/clickqt/actions/workflows/ci.yml)
[![Documentation Status](https://readthedocs.org/projects/clickqt/badge/)](https://clickqt.readthedocs.io/)

**This is currently under active development between myself and a group of students**

## Installation

The Python packaage `clickqt` can be installed from PyPI:

```
python -m pip install clickqt
```

## Development installation

If you want to contribute to the development of `clickqt`, we recommend
the following editable installation from this repository:

```
git clone git@github.com:dokempf/clickqt.git
cd clickqt
python -m pip install --editable .[tests]
```

Having done so, the test suite can be run using `pytest`:

```
python -m pytest
```

## Acknowledgments

This repository was set up using the [SSC Cookiecutter for Python Packages](https://github.com/ssciwr/cookiecutter-python-package).
