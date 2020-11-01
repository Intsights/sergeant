<p align="center">
    <a href="https://github.com/intsights/sergeant">
        <img src="https://raw.githubusercontent.com/intsights/sergeant/master/images/logo.png" alt="Logo">
    </a>
    <h3 align="center">
        Fast, Safe & Simple Asynchronous Task Queues Written In Pure Python
    </h3>
</p>

![license](https://img.shields.io/badge/MIT-License-blue)
![Python](https://img.shields.io/badge/Python-3.7%20%7C%203.8%20%7C%203.9-blue)
![Build](https://github.com/intsights/sergeant/workflows/Build/badge.svg)
[![PyPi](https://img.shields.io/pypi/v/sergeant.svg)](https://pypi.org/project/sergeant/)

## Table of Contents

- [Table of Contents](#table-of-contents)
- [About The Project](#about-the-project)
  - [Built With](#built-with)
  - [Performance](#performance)
  - [Installation](#installation)
- [Documentation](#documentation)
- [Usage](#usage)
- [License](#license)
- [Contact](#contact)


## About The Project

`Sergeant` is a comprehensive distributed workers framework. The library was written in [Intsights](https://intsights.com/) after failing to use `celery` with high scale. The library focuses on process and thread safety (through process/thread killers), performance and ease of use.


### Built With

* [orjson](https://github.com/ijl/orjson)
* [msgpack](https://github.com/msgpack/msgpack-python)
* [pymongo](https://github.com/mongodb/mongo-python-driver)
* [redis](https://github.com/andymccurdy/redis-py)
* [psutil](https://github.com/giampaolo/psutil)


### Performance

Benchmark code can be found inside `benchmark` directory.


### Installation

```sh
pip3 install sergeant
```


## Documentation

More information can be found on the [documentation](https://intsights.github.io/sergeant/) site.

## Usage

Usage examples can be found inside `examples` directory.


## License

Distributed under the MIT License. See `LICENSE` for more information.


## Contact

Gal Ben David - gal@intsights.com

Project Link: [https://github.com/intsights/sergeant](https://github.com/intsights/sergeant)
