import argparse
import ctypes
import enum
import importlib
import multiprocessing.connection
import os
import signal
import sys
import threading
import traceback
import typing


class ReturnCode(
    enum.Enum,
):
    WORKER_EXITED_NORMALLY: int = 0
    WORKER_EXITED_ABNORMALLY: int = 1
    WORKER_MODULE_NOT_FOUND: int = 2
    WORKER_CLASS_NOT_FOUND: int = 3
    WORKER_ASKED_TO_RESPAWN: int = 4
    WORKER_ASKED_TO_STOP: int = 5
    WORKER_EXECUTION_FAILURE: int = 6
    WORKER_MODULE_NOT_IMPORTABLE: int = 7


def work(
    worker_module_name: str,
    worker_class_name: str,
) -> typing.Tuple[int, typing.Optional[typing.Dict[str, typing.Any]]]:
    try:
        worker_module = importlib.import_module(
            name=worker_module_name,
        )
    except ModuleNotFoundError:
        return (
            ReturnCode.WORKER_MODULE_NOT_FOUND.value,
            None,
        )
    except Exception as exception:
        return (
            ReturnCode.WORKER_MODULE_NOT_IMPORTABLE.value,
            {
                'exception': repr(exception),
                'stacktrace': traceback.format_exc(),
            },
        )

    try:
        worker_class = getattr(worker_module, worker_class_name)
    except AttributeError:
        return (
            ReturnCode.WORKER_CLASS_NOT_FOUND.value,
            None,
        )

    try:
        worker_obj = worker_class()
        worker_obj.init_worker()
        summary = worker_obj.work_loop()

        if summary['respawn']:
            return (
                ReturnCode.WORKER_ASKED_TO_RESPAWN.value,
                summary,
            )
        elif summary['stop']:
            return (
                ReturnCode.WORKER_ASKED_TO_STOP.value,
                summary,
            )
        elif (
            summary['executor_exception'] or
            summary['initialize_exception'] or
            summary['finalize_exception']
        ):
            return (
                ReturnCode.WORKER_EXECUTION_FAILURE.value,
                summary,
            )
        else:
            return (
                ReturnCode.WORKER_EXITED_NORMALLY.value,
                summary,
            )
    except Exception as exception:
        return (
            ReturnCode.WORKER_EXITED_ABNORMALLY.value,
            {
                'exception': repr(exception),
                'stacktrace': traceback.format_exc(),
            },
        )


def kill_running_background_threads() -> bool:
    number_of_unkillable_threads = 0
    for thread in threading.enumerate():
        if thread is threading.main_thread():
            continue

        if thread.ident:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_ulong(thread.ident),
                ctypes.py_object(SystemExit),
            )

            thread.join(
                timeout=2.0,
            )
            if thread.is_alive():
                number_of_unkillable_threads += 1

    return number_of_unkillable_threads == 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Sergeant Slave',
    )
    parser.add_argument(
        '--child-pipe',
        help='Pipe fileno to return the potential exception',
        type=int,
        required=True,
        dest='child_pipe',
    )
    parser.add_argument(
        '--worker-class',
        help='Class name of the worker to spawn',
        type=str,
        required=True,
        dest='worker_class',
    )
    parser.add_argument(
        '--worker-module',
        help='Module of the worker class',
        type=str,
        required=True,
        dest='worker_module',
    )
    args = parser.parse_args()

    try:
        pipe_obj = multiprocessing.connection.Connection(
            handle=args.child_pipe,
        )

        return_code, summary = work(
            worker_module_name=args.worker_module,
            worker_class_name=args.worker_class,
        )
        if not summary:
            sys.exit(return_code)

        summary['return_code'] = return_code

        background_threads_killed_successfully = kill_running_background_threads()
        if not background_threads_killed_successfully:
            unkillable_threads = [
                thread.name
                for thread in threading.enumerate()
                if thread is not threading.main_thread()
            ]
            summary['unkillable_threads'] = unkillable_threads

            pipe_obj.send(summary)
            pipe_obj.close()

            os.kill(os.getpid(), signal.SIGKILL)
        else:
            pipe_obj.send(summary)
            pipe_obj.close()

            sys.exit(return_code)
    except KeyboardInterrupt:
        sys.exit(0)
