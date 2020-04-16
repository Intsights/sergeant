import sys
import os
import multiprocessing
import subprocess
import shlex
import multiprocessing.context
import traceback
import argparse
import logging
import psutil
import time


class SupervisedWorker:
    def __init__(
        self,
        worker_module_name,
        worker_class_name,
    ):
        pipe = multiprocessing.Pipe()

        self.parent_pipe = pipe[0]
        self.child_pipe = pipe[1]
        self._exception = None

        self.process = subprocess.Popen(
            args=shlex.split(
                s=f'python3 -m sergeant.slave --child-pipe={self.child_pipe.fileno()} --worker-module={worker_module_name} --worker-class={worker_class_name}',
            ),
            pass_fds=(
                self.child_pipe.fileno(),
            ),
        )

        self.psutil_obj = psutil.Process(
            pid=self.process.pid,
        )

    @property
    def rss_memory(
        self,
    ):
        try:
            return self.psutil_obj.memory_info().rss
        except psutil.NoSuchProcess:
            return 0

    @property
    def exception(
        self,
    ):
        try:
            if self.parent_pipe.poll():
                self._exception = self.parent_pipe.recv()

            return self._exception
        except Exception as exception:
            return {
                'exception': exception,
                'traceback': traceback.format_exc(),
            }

    def kill(
        self,
    ):
        try:
            self.child_pipe.close()
            self.parent_pipe.close()
        except Exception:
            pass

        try:
            self.process.terminate()
        except Exception:
            pass

        try:
            self.process.wait()
        except (
            ChildProcessError,
            OSError,
        ):
            pass

    def __del__(
        self,
    ):
        self.kill()


class Supervisor:
    def __init__(
        self,
        worker_module_name,
        worker_class_name,
        concurrent_workers,
        max_worker_memory_usage,
    ):
        self.worker_module_name = worker_module_name
        self.worker_class_name = worker_class_name
        self.concurrent_workers = concurrent_workers
        self.max_worker_memory_usage = max_worker_memory_usage

        self.logger = logging.getLogger(
            name='Supervisor',
        )

        formatter = logging.Formatter(
            fmt='%(asctime)s %(name)-12s %(process)d %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)
        self.logger.setLevel(logging.INFO)

        self.current_workers = []

    def start(
        self,
    ):
        for i in range(self.concurrent_workers):
            worker = SupervisedWorker(
                worker_module_name=self.worker_module_name,
                worker_class_name=self.worker_class_name,
            )
            self.logger.info(f'spawned a new worker at pid: {worker.process.pid}')

            self.current_workers.append(worker)

        self.supervise_loop()

    def supervise_loop(
        self,
    ):
        try:
            while True:
                current_workers = self.current_workers.copy()
                for worker in current_workers:
                    self.supervise_worker(
                        worker=worker,
                    )

                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        except Exception as exception:
            self.logger.error(f'the supervisor encountered an exception: {exception}')
            self.logger.error(f'exiting...')
        finally:
            for worker in self.current_workers:
                self.logger.info(f'killing a worker: {worker.process.pid}')
                worker.kill()
            sys.exit(0)

    def supervise_worker(
        self,
        worker,
    ):
        if worker.process.poll() is not None:
            self.logger.info(f'a worker has exited with error code: {worker.process.returncode}')
            try:
                os.waitpid(worker.process.pid, 0)
            except ChildProcessError:
                pass

            if worker.process.returncode == 2:
                self.logger.error(f'could not load worker module: {self.worker_module_name}')

                sys.exit(1)

            if worker.process.returncode == 3:
                self.logger.error(f'could not find worker class: {self.worker_module_name}.{self.worker_class_name}')

                sys.exit(1)

            if worker.exception:
                self.logger.error(f'worker exception: {worker.exception["exception"]}')
                self.logger.error(f'worker traceback:\n{worker.exception["traceback"]}')

            self.respawn_a_worker(
                worker=worker,
            )

        if self.max_worker_memory_usage:
            if worker.rss_memory > self.max_worker_memory_usage:
                self.logger.info(f'worker exceeded the maximum memory limit: pid: {worker.process.pid}, rss: {worker.rss_memory}')
                self.respawn_a_worker(
                    worker=worker,
                )

    def respawn_a_worker(
        self,
        worker,
    ):
        worker.kill()
        self.current_workers.remove(worker)
        worker = SupervisedWorker(
            worker_module_name=self.worker_module_name,
            worker_class_name=self.worker_class_name,
        )
        self.logger.info(f'spawned a new worker at pid: {worker.process.pid}')
        self.current_workers.append(worker)


def main():
    parser = argparse.ArgumentParser(
        description='Sergeant Supervisor',
    )
    parser.add_argument(
        '--concurrent-workers',
        help='Number of subprocesses to open',
        type=int,
        required=True,
        dest='concurrent_workers',
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
    parser.add_argument(
        '--max-worker-memory-usage',
        help='Maximum RSS memory usage in bytes of an individual worker. When a worker reaches this value, the supevisor would kill it and respawn another one in place.',
        type=int,
        required=False,
        dest='max_worker_memory_usage',
    )
    args = parser.parse_args()

    supervisor = Supervisor(
        worker_module_name=args.worker_module,
        worker_class_name=args.worker_class,
        concurrent_workers=args.concurrent_workers,
        max_worker_memory_usage=args.max_worker_memory_usage,
    )
    supervisor.start()


if __name__ == '__main__':
    main()
