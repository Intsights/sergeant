import argparse
import importlib
import multiprocessing.connection
import sys
import traceback


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Sergeant Supervisor',
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
    pipe_obj = multiprocessing.connection.Connection(
        handle=args.child_pipe,
    )

    try:
        worker_module = importlib.import_module(
            name=args.worker_module,
        )
    except ModuleNotFoundError:
        return 2

    try:
        worker_class = getattr(worker_module, args.worker_class)
    except AttributeError:
        return 3

    try:
        worker_obj = worker_class()
        worker_obj.init_worker()
        summary = worker_obj.work_loop()
        pipe_obj.send(summary)

        if summary['respawn']:
            return 4
        elif summary['stop']:
            return 5
        else:
            return 0
    except KeyboardInterrupt:
        return 0
    except Exception as exception:
        pipe_obj.send(
            {
                'message': str(exception),
                'stacktrace': traceback.format_exc(),
                'type': exception.__class__.__name__,
            },
        )

        return 1
    finally:
        try:
            pipe_obj.close()
        except Exception:
            pass


if __name__ == '__main__':
    sys.exit(main())
