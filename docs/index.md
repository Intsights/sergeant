<p align="center">
    <a href="https://github.com/intsights/sergeant">
        <img src="https://raw.githubusercontent.com/intsights/sergeant/master/images/logo.png" alt="Logo">
    </a>
    <h3 align="center">
        Fast, Safe & Simple Asynchronous Task Queues Written In Pure Python
    </h3>
</p>


# Home
`Sergeant` was written in Insights when `Celery` failed to work on large scales. At a peak, we had over 100k tasks per second and thousands of workers. Celery was unreliable on that scale. Compared to `celery`, `Sergeant` is simpler and easier to understand. This library offers a simple and intuitive interface to implement a queue-based distributed workers architecture instead of supporting a variety of backends and scenarios. `Redis` and `MongoDB` are the two supported server backends. `Redis` is recommended for high throughput environments where performance is paramount. Whenever you need to save your tasks on the disk, you should use `MongoDB` for stable, consistent systems. There is a third backend called `local` which is based on SQLite3 database file. We decided not to support AMQP backends in order to keep the library simple. Using some of Python's latest features, such as `dataclasses` and `f-strings`, this library is only compatible with `Python 3.7` and up.

Multiple serializers and compressions are provided by the library. Before pushing a job into the queue, the library serializes it and optionally compresses it. `pickle` and `msgpack` are available serializers. The default serializer `pickle` should not be switched unless it has some limitations, such as security concerns or portability issues. Different serializers support different types of data. Even though Pickle is not portable, it handles more data types than any other serializer. The serialization and deserialization of tasks with parameters not supported by msgpack must be done manually or using Pickle.

This library includes multiple built-in compression algorithms that are natively supported by Python. `zlib`, `gzip`, `bzip2` and `lzma`. When `None` is selected, no compression is performed. If you have a lot of tasks queued and need to free up some RAM/storage, using a compressor is recommended.

Tasks can be executed using either multiprocessing or threading. Each task may be executed in a different thread or process, depending on the implementor. Concurrency levels can be configured.

The library provides two watchdog mechanisms to prevent situations where tasks are running for longer than expected. The first mechanism is a process killer. To ensure that tasks do not exceed the specified maximum timeout, a separate process is created that watches for starting and stopping signals. A thread killer is spawned when using a threading executor. The nature of Python threads means that this killer can only raise an exception in the context of the watched thread. This killer will not work in situations where the thread locks the GIL, such as when executing an infinite regex. Threaded executors should be used with caution.

The `Supervisor` is responsible for managing workers. The supervisor spawns the child workers, each in a different process, and waits for their execution to be completed. Upon completion, the supervisor spawns another child in place of the worker. He also takes care of an out of bounds worker. A worker which violates some optional violations is being killed and replaced with another one. You can specify a memory usage limit.
