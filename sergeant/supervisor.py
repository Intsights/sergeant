import typing
import sys
import os
import multiprocessing
import subprocess
import shlex
import multiprocessing.context
import argparse
import logging
import psutil
import time


class SupervisedWorker:
    def __init__(
        self,
        worker_module_name: str,
        worker_class_name: str,
    ):
        self.logger = logging.getLogger(
            name='SupervisedWorker',
        )

        pipe = multiprocessing.Pipe()

        self.parent_pipe = pipe[0]
        self.child_pipe = pipe[1]

        self.process = subprocess.Popen(
            args=shlex.split(
                s=(
                    f'{sys.executable} -m sergeant.slave '
                    f'--worker-module={worker_module_name} '
                    f'--worker-class={worker_class_name} '
                    f'--child-pipe={self.child_pipe.fileno()} '
                ),
            ),
            pass_fds=(
                self.child_pipe.fileno(),
            ),
        )

        self.psutil_obj = psutil.Process(
            pid=self.process.pid,
        )

    def get_rss_memory(
        self,
    ) -> int:
        try:
            return self.psutil_obj.memory_info().rss
        except psutil.NoSuchProcess:
            return 0

    def get_summary(
        self,
    ) -> typing.Optional[typing.Dict[str, typing.Any]]:
        try:
            if self.parent_pipe.poll():
                return self.parent_pipe.recv()
            else:
                return None
        except Exception as exception:
            self.logger.error(f'could not receive supervised_worker\'s summary: {exception}')

            return None

    def kill(
        self,
    ) -> None:
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
    ) -> None:
        self.kill()


class Supervisor:
    def __init__(
        self,
        worker_module_name: str,
        worker_class_name: str,
        concurrent_workers: int,
        max_worker_memory_usage: typing.Optional[int] = None,
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
    ) -> None:
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
    ) -> None:
        try:
            while self.current_workers:
                current_workers = self.current_workers.copy()
                for worker in current_workers:
                    self.supervise_worker(
                        worker=worker,
                    )

                time.sleep(0.5)

            self.logger.info(f'no more workers to supervise')
        except KeyboardInterrupt:
            pass
        except Exception as exception:
            self.logger.error(f'the supervisor encountered an exception: {exception}')
        finally:
            for worker in self.current_workers:
                self.logger.info(f'killing a worker: {worker.process.pid}')
                worker.kill()

            self.logger.info(f'exiting...')
            sys.exit(0)

    def supervise_worker(
        self,
        worker: SupervisedWorker,
    ) -> None:
        if worker.process.poll() is not None:
            worker_summary = worker.get_summary()

            self.logger.info(f'a worker has exited with error code: {worker.process.returncode}')

            try:
                os.waitpid(worker.process.pid, 0)
            except ChildProcessError:
                pass

            if worker.process.returncode == 0:
                if worker_summary:
                    self.logger.debug(f'worker summary: {worker_summary}')
                else:
                    self.logger.debug(f'worker summary is unavailable')
            elif worker.process.returncode == 1:
                self.logger.error(f'worker execution has failed')

                if worker_summary:
                    self.logger.error(f'exception: {worker_summary["exception"]}')
                    self.logger.error(f'traceback: {worker_summary["traceback"]}')
                else:
                    self.logger.error(f'exception and tracback are unavailable')
            elif worker.process.returncode == 2:
                self.logger.error(f'could not load worker module: {self.worker_module_name}')

                sys.exit(1)
            elif worker.process.returncode == 3:
                self.logger.error(f'could not find worker class: {self.worker_module_name}.{self.worker_class_name}')

                sys.exit(1)
            elif worker.process.returncode == 4:
                self.logger.info(f'worker has requested to respawn')
            elif worker.process.returncode == 5:
                self.logger.info(f'worker has requested to stop')

                self.stop_a_worker(
                    worker=worker,
                )

                return

            self.respawn_a_worker(
                worker=worker,
            )

        if self.max_worker_memory_usage:
            if worker.get_rss_memory() > self.max_worker_memory_usage:
                self.logger.info(f'worker exceeded the maximum memory limit: pid: {worker.process.pid}, rss: {worker.get_rss_memory()}')
                self.respawn_a_worker(
                    worker=worker,
                )

    def respawn_a_worker(
        self,
        worker: SupervisedWorker,
    ) -> None:
        worker.kill()
        self.current_workers.remove(worker)
        new_worker = SupervisedWorker(
            worker_module_name=self.worker_module_name,
            worker_class_name=self.worker_class_name,
        )
        self.logger.info(f'spawned a new worker at pid: {new_worker.process.pid}')
        self.current_workers.append(new_worker)

    def stop_a_worker(
        self,
        worker: SupervisedWorker,
    ) -> None:
        worker.kill()
        self.current_workers.remove(worker)
        self.logger.info(f'worker has stopped: {worker.process.pid}')


def main() -> None:
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
