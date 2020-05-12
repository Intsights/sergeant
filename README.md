<p align="center">
    <a href="https://github.com/intsights/sergeant">
        <img src="https://raw.githubusercontent.com/intsights/sergeant/master/images/logo.png" alt="Logo">
    </a>
    <h3 align="center">
        Fast, Safe & Simple Asynchronous Task Queues Written In Pure Python
    </h3>
</p>

![license](https://img.shields.io/badge/MIT-License-blue)
![Python](https://img.shields.io/badge/Python-3.7%20%7C%203.8-blue)
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

`Sergeant` is a library that was written at `Intsights` after failing to use `celery` at high scale. Our infrastructure had peaks of more than 100k tasks a second and thousands of workers. Celery found to be slow and unstable for that scale. `Sergeant` as opposed to `celery` is much simpler and easier. Instead of supporting a wide range of backends and scenarios, this library provides a simple and intuitive interface to implement a queue-based asynchronous workers architecture. The two supported backends are `redis` and `mongo`. Redis as an in-memory database, is recommended for high throughput environments, where performance is the top priority. Mongo is recommended for stable and consistent systems where you need tasks to be kept persistently. The decision not to support AMQP based backends was decided in order to leave this library as simple as possible and to leave the ability to build more complex mechanisms to the user. The library uses some latest python features such as `dataclasses` and `f-strings`, which makes this library to be compatible only with `Python 3.7+`.

The library supports multiple serializers and compressions. Each task, prior to being pushed into the queue, should be serialized, and optionally compressed. The supported serializers are `pickle` and `msgpack`. One should not switch the default serializer `pickle` unless it has some limitations such as security concerns, or programming languages portability issues. You should remember the each serializer supported different data types. While pickle is not portable, it support much more types than any other serializer. When executing tasks with parameters that are not supported by msgpack, you should serialize/deserialize manually, or use pickle.

As for the compressions, this library support multiple built-in compressions algorithms that are supported natively by Python. `zlib`, `gzip`, `bzip2` and `lzma`. The default compressor is `None` which does not compress at all. One should choose a different compressor to reduce the amount of RAM (when using Redis) and storage (when using mongo) if it has a huge amount of tasks being stored when the system is at peak capacity.

The library tasks execution supported mechanisms are `multiprocessing` and `threading`. This means that each task might be executed, according to the choice of the implementor, in a different thread, or different process. The concurrency level is configurable.

The library supports two watchdogs mechanisms to evade situations where the tasks are running for a longer time than expected. The first is a process killer. This type of watchdog spawns a separated process which waits for start and stop signals to make sure the tasks did not exceed the specified maximum timeout. When using a threading executor, a thread killer is being spawned. Due to the nature of threads in python, this killer has only one ability, and it is to raise an Exception in the context of the watched thread. In situations where the thread locks the GIL, like executing an infinite regex, this killer will fail at its job. Choosing a threaded executor should be taken with caution.

The main process which takes care of the worker is the `supervisor`. The supervisor spawns the child workers, each one in a different process, and waits for their execution to complete. Once completed, the supervisor spawns another child in place of the worker. The supervisor also takes care of an out of bound workers. A worker which violates some optional violations is being killed and replaced with another one. You can specify a memory usage limit.


### Built With

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
