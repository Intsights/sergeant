import argparse
import logging
import multiprocessing
import multiprocessing.connection
import os
import psutil
import shlex
import subprocess
import sys
import time


class KillerServer:
    def __init__(
        self,
        pipe: multiprocessing.connection.Connection,
        pid_to_kill: int,
        sleep_interval: float,
        timeout: float,
        grace_period: float,
    ) -> None:
        self.init_logger()

        self.pipe = pipe
        self.process_to_kill = psutil.Process(
            pid=pid_to_kill,
        )

        self.sleep_interval = sleep_interval
        self.time_elapsed = 0.0

        self.timeout = timeout
        self.critical_timeout = timeout + grace_period

        self.timeout_raised = False
        self.critical_timeout_raised = False

        self.running = False
        self.kill_received = False
        self.shutdown_received = False
        self.pipe_was_closed = False

    def init_logger(
        self,
    ) -> None:
        self.logger = logging.getLogger(
            name='Killer',
        )
        self.logger.propagate = False
        self.logger.setLevel(
            level=logging.ERROR,
        )
        stream_handler = logging.StreamHandler(
            stream=sys.stdout,
        )
        stream_handler.setFormatter(
            fmt=logging.Formatter(
                fmt='%(asctime)s %(name)-12s %(process)d %(levelname)-8s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
            ),
        )
        self.logger.addHandler(
            hdlr=stream_handler,
        )

    def process_requests(
        self,
    ) -> None:
        if self.pipe.poll(
            timeout=self.sleep_interval,
        ):
            try:
                data = self.pipe.recv_bytes()
                if data == b'start':
                    self.logger.info(
                        msg='start request was received',
                    )
                    self.running = True
                elif data == b'stop':
                    self.logger.info(
                        msg='stop request was received',
                    )
                    self.running = False
                elif data == b'reset':
                    self.logger.info(
                        msg='reset request was received',
                    )
                    self.time_elapsed = 0.0
                    self.timeout_raised = False
                    self.critical_timeout_raised = False
                elif data == b'stop_and_reset':
                    self.logger.info(
                        msg='stop_and_reset request was received',
                    )
                    self.running = False
                    self.time_elapsed = 0.0
                    self.timeout_raised = False
                    self.critical_timeout_raised = False
                elif data == b'shutdown':
                    self.logger.info(
                        msg='shutdown request was received',
                    )
                    self.shutdown_received = True
                elif data == b'kill':
                    self.logger.info(
                        msg='kill request was received',
                    )
                    self.kill_received = True
            except EOFError:
                self.logger.warning(
                    msg='recv_bytes has exited unexpectedly with EOFError',
                )
                self.pipe_was_closed = True

    def kill_loop(
        self,
    ) -> None:
        self.logger.info(
            msg='kill loop started',
        )

        while self.is_process_alive(
            process=self.process_to_kill,
        ):
            before = time.time()

            self.process_requests()

            if self.kill_received:
                break
            elif self.pipe_was_closed or self.shutdown_received:
                self.logger.info(
                    msg='waiting for process to terminate',
                )
                try:
                    self.process_to_kill.wait(
                        timeout=10,
                    )
                except psutil.TimeoutExpired:
                    self.kill_process_and_children()

                break
            elif self.running:
                if not self.timeout_raised and self.time_elapsed >= self.timeout:
                    self.logger.info(
                        msg='sending timeout signal',
                    )
                    self.timeout_raised = True

                    try:
                        self.process_to_kill.terminate()
                    except Exception as exception:
                        self.logger.error(
                            msg=f'sending timeout raised: {exception}',
                        )
                elif not self.critical_timeout_raised and self.time_elapsed >= self.critical_timeout:
                    self.logger.info(
                        msg='sending critical timeout signal',
                    )
                    self.critical_timeout_raised = True
                    self.kill_process_and_children()

                    break

                after = time.time()
                self.time_elapsed += after - before

        self.logger.info(
            msg='kill loop ended',
        )

    def is_process_alive(
        self,
        process: psutil.Process,
    ) -> bool:
        if not process.is_running():
            self.logger.info(
                msg='process status: not running',
            )

            return False

        try:
            process_status = process.status()
        except psutil.NoSuchProcess:
            self.logger.info(
                msg='pid does not exist anymore',
            )

            return False

        if process_status in [
            psutil.STATUS_DEAD,
            psutil.STATUS_ZOMBIE,
        ]:
            self.logger.info(
                msg=f'process became a zombie/dead process: {process_status}',
            )

            return False

        return True

    def kill_process_and_children(
        self,
    ) -> None:
        processes_to_kill = self.process_to_kill.children(
            recursive=True,
        )
        processes_to_kill.append(self.process_to_kill)
        processes_to_kill = [
            process_to_kill
            for process_to_kill in processes_to_kill
            if process_to_kill.pid != os.getpid()
        ]

        for process_to_kill in processes_to_kill:
            try:
                process_to_kill.kill()
            except psutil.NoSuchProcess as exception:
                self.logger.error(
                    msg=f'No process to kill: {exception}',
                )

        psutil.wait_procs(
            procs=processes_to_kill,
            timeout=1.0,
        )

        self.logger.info(
            msg='process and child processes were killed',
        )


class Killer:
    def __init__(
        self,
        pid_to_kill: int,
        sleep_interval: float,
        timeout: float,
        grace_period: float,
    ) -> None:
        self.parent_pipe: multiprocessing.connection.Connection
        self.child_pipe: multiprocessing.connection.Connection
        self.parent_pipe, self.child_pipe = multiprocessing.Pipe()

        self.killer_process = subprocess.Popen(
            args=shlex.split(
                s=(
                    f'{sys.executable} {os.path.relpath(__file__)} '
                    f'--pid-to-kill {pid_to_kill} '
                    f'--sleep-interval {sleep_interval} '
                    f'--timeout {timeout} '
                    f'--grace-period {grace_period} '
                    f'--pipe-fd {self.child_pipe.fileno()} '
                ),
            ),
            pass_fds=[
                self.child_pipe.fileno(),
            ],
        )

        self.parent_pipe.recv()

    def start(
        self,
    ) -> None:
        self.parent_pipe.send_bytes(b'start')

    def stop(
        self,
    ) -> None:
        self.parent_pipe.send_bytes(b'stop')

    def reset(
        self,
    ) -> None:
        self.parent_pipe.send_bytes(b'reset')

    def stop_and_reset(
        self,
    ) -> None:
        self.parent_pipe.send_bytes(b'stop_and_reset')

    def shutdown(
        self,
    ) -> None:
        self.parent_pipe.send_bytes(b'shutdown')

    def kill(
        self,
    ) -> None:
        self.parent_pipe.send_bytes(b'kill')

        try:
            self.killer_process.wait(
                timeout=2.0,
            )
        except Exception:
            pass

    def __del__(
        self,
    ) -> None:
        try:
            self.kill()
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(
        description='Process Killer',
    )
    parser.add_argument(
        '--pid-to-kill',
        help='pid to kill on timeouts',
        type=int,
        required=True,
        dest='pid_to_kill',
    )
    parser.add_argument(
        '--sleep-interval',
        help='time to sleep between checks',
        type=float,
        required=True,
        dest='sleep_interval',
    )
    parser.add_argument(
        '--timeout',
        help='timeout',
        type=float,
        required=True,
        dest='timeout',
    )
    parser.add_argument(
        '--grace-period',
        help='grace period',
        type=float,
        required=True,
        dest='grace_period',
    )
    parser.add_argument(
        '--pipe-fd',
        help='file descriptor of a pipe to hand over the port',
        type=int,
        required=True,
        dest='pipe_fd',
    )

    args = parser.parse_args()

    pipe = multiprocessing.connection.Connection(
        handle=args.pipe_fd,
    )
    pipe.send(
        obj={},
    )

    killer_server = KillerServer(
        pipe=pipe,
        pid_to_kill=args.pid_to_kill,
        sleep_interval=args.sleep_interval,
        timeout=args.timeout,
        grace_period=args.grace_period,
    )
    killer_server.kill_loop()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
