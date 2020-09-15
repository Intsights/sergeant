<p align="center">
    <a href="https://github.com/intsights/sergeant">
        <img src="https://raw.githubusercontent.com/intsights/sergeant/master/images/logo.png" alt="Logo">
    </a>
    <h3 align="center">
        Fast, Safe & Simple Asynchronous Task Queues Written In Pure Python
    </h3>
</p>


# Home
`Sergeant` was written in `Intsights` after failing to use `celery` with large scale. Our infrastructure had peaks of more than 100k tasks a second and thousands of workers. We found Celery to be slow and unstable at that scale. `Sergeant` as opposed to `celery` is much simpler and more accessible. Instead of supporting a wide range of backends and scenarios, this library provides a simple and intuitive interface to implement a queue-based distributed workers architecture. The two supported backends are `redis` and `mongo`. As an in-memory database, Redis is recommended for high throughput environments, where performance is the top priority. Mongo is recommended for stable and consistent systems where you need your tasks to be saved on the disk. In order to keep the library simple, we decided not to support AMQP backends. The library uses some latest python features such as `dataclasses` and `f-strings`, making this library compatible only with `Python 3.7` and up.

The library supports multiple serializers and compressions.Before pushing a task into the queue, the library serializes the job and optionally compresses it. The supported serializers are `pickle` and `msgpack`. One should not switch the default serializer `pickle` unless it has some limitations, such as security concerns or portability reasons. Each serializer supports different data types. While pickle is not portable, it supports broader data types than any other serializer. Executing tasks with parameters that are not supported by msgpack requires serializing/deserializing manually or using pickle.

As for the compressions, this library support multiple built-in compressions algorithms that are supported natively by Python. `zlib`, `gzip`, `bzip2` and `lzma`. The default compressor is `None` which does not compress at all. Using a compressor is encouraged when you have a massive amount of tasks in your queues, and you want to spare RAM/Storage.

The library tasks execution supported mechanisms are `multiprocessing` and `threading`. This means that each task might be executed according to the implementor's choice, in a different thread, or different process. The concurrency level is configurable.

The library supports two watchdogs mechanisms to evade situations where the tasks are running for a longer time than expected. The first is a process killer. This watchdog spawns a separated process that waits for starts and stops signals to ensure the tasks did not exceed the specified maximum timeout. When using a threading executor, a thread killer is being spawned. Due to the nature of threads in Python, this killer has only one ability, and it is to raise an Exception in the context of the watched thread. In situations where the thread locks the GIL, like executing an infinite regex, this killer will fail at its job. Choosing a threaded executor should be taken with caution.

The primary process which takes care of the worker is the `supervisor`. The supervisor spawns the child workers, each one in a different process, and waits for their execution to complete. Once completed, the supervisor spawns another child in place of the worker. The supervisor also takes care of an out of bound workers. A worker which violates some optional violations is being killed and replaced with another one. You can specify a memory usage limit.
