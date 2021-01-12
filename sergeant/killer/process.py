import argparse
import logging
import multiprocessing
import multiprocessing.connection
import os
import psutil
import shlex
import signal
import subprocess
import sys
import time


class KillerServer:
    def __init__(
        self,
        pipe: multiprocessing.connection.Connection,
        pid_to_kill: int,
        sleep_interval: float,
        soft_timeout: float,
        hard_timeout: float,
        critical_timeout: float,
    ) -> None:
        self.init_logger()

        self.pipe = pipe
        self.process_to_kill = psutil.Process(
            pid=pid_to_kill,
        )

        self.sleep_interval = sleep_interval
        self.time_elapsed = 0.0

        self.soft_timeout = soft_timeout
        self.hard_timeout = hard_timeout
        self.critical_timeout = critical_timeout

        self.soft_timeout_raised = False
        self.hard_timeout_raised = False
        self.critical_timeout_raised = False

        self.running = False
        self.kill_received = False

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
    ) -> bool:
        if self.pipe.poll(
            timeout=self.sleep_interval,
        ):
            try:
                data = self.pipe.recv_bytes()
            except EOFError:
                self.logger.warning(
                    msg='recv_bytes has exited unexpectedly with EOFError',
                )

                return False

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
                self.soft_timeout_raised = False
                self.hard_timeout_raised = False
                self.critical_timeout_raised = False
            elif data == b'stop_and_reset':
                self.logger.info(
                    msg='stop_and_reset request was received',
                )
                self.running = False
                self.time_elapsed = 0.0
                self.soft_timeout_raised = False
                self.hard_timeout_raised = False
                self.critical_timeout_raised = False
            elif data == b'kill':
                self.logger.info(
                    msg='kill request was received',
                )
                self.kill_received = True

                return False

        return True

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

            if not self.process_requests():
                break

            if self.running:
                self.check_and_process_soft_timeout()
                self.check_and_process_hard_timeout()
                self.check_and_process_critical_timeout()

                after = time.time()
                self.time_elapsed += after - before

        if self.kill_received is False:
            try:
                self.logger.info(
                    msg='waiting for process to terminate',
                )
                self.process_to_kill.wait(
                    timeout=5.0,
                )
            except Exception:
                self.logger.warning(
                    msg='waiting for process to terminate has timedout. killing...',
                )
                self.kill_process(
                    process=self.process_to_kill,
                    signal_code=signal.SIGKILL,
                )

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

    def check_and_process_soft_timeout(
        self,
    ) -> None:
        if not self.soft_timeout:
            return

        if self.soft_timeout_raised:
            return

        if self.time_elapsed >= self.soft_timeout:
            self.logger.info(
                msg='raising soft timeout',
            )
            self.soft_timeout_raised = True
            self.kill_process(
                process=self.process_to_kill,
                signal_code=signal.SIGINT,
            )

    def check_and_process_hard_timeout(
        self,
    ) -> None:
        if not self.hard_timeout:
            return

        if self.hard_timeout_raised:
            return

        if self.time_elapsed >= self.hard_timeout:
            self.logger.info(
                msg='raising hard timeout',
            )
            self.hard_timeout_raised = True
            self.kill_process(
                process=self.process_to_kill,
                signal_code=signal.SIGABRT,
            )

    def check_and_process_critical_timeout(
        self,
    ) -> None:
        if not self.critical_timeout:
            return

        if self.critical_timeout_raised:
            return

        if self.time_elapsed >= self.critical_timeout:
            self.logger.info(
                msg='raising critical timeout',
            )
            self.critical_timeout_raised = True
            self.kill_process(
                process=self.process_to_kill,
                signal_code=signal.SIGKILL,
            )

    def kill_process(
        self,
        process: psutil.Process,
        signal_code: int,
    ) -> None:
        try:
            self.logger.info(
                msg='kill_process request',
            )

            process.send_signal(
                sig=signal_code,
            )
        except Exception as exception:
            self.logger.error(
                msg=f'could not kill process: {exception}',
            )

        try:
            if signal_code == signal.SIGKILL:
                process.wait(
                    timeout=0.1,
                )
        except Exception:
            pass


class Killer:
    def __init__(
        self,
        pid_to_kill: int,
        sleep_interval: float,
        soft_timeout: float,
        hard_timeout: float,
        critical_timeout: float,
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
                    f'--soft-timeout {soft_timeout} '
                    f'--hard-timeout {hard_timeout} '
                    f'--critical-timeout {critical_timeout} '
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

    def kill(
        self,
    ) -> None:
        self.parent_pipe.send_bytes(b'kill')

        try:
            self.killer_process.wait(
                timeout=1.0,
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
        '--soft-timeout',
        help='soft timeout',
        type=float,
        required=True,
        dest='soft_timeout',
    )
    parser.add_argument(
        '--hard-timeout',
        help='hard timeout',
        type=float,
        required=True,
        dest='hard_timeout',
    )
    parser.add_argument(
        '--critical-timeout',
        help='critical timeout',
        type=float,
        required=True,
        dest='critical_timeout',
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
        soft_timeout=args.soft_timeout,
        hard_timeout=args.hard_timeout,
        critical_timeout=args.critical_timeout,
    )
    killer_server.kill_loop()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
