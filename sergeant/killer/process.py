import typing
import os
import signal
import asyncio
import subprocess
import multiprocessing
import multiprocessing.connection
import shlex
import sys
import psutil
import argparse
import socket
import logging


class KillerServer(
    asyncio.DatagramProtocol,
):
    def __init__(
        self,
        async_loop: asyncio.AbstractEventLoop,
        pid_to_kill: int,
        sleep_interval: float,
        soft_timeout: float,
        hard_timeout: float,
        critical_timeout: float,
    ) -> None:
        super().__init__()

        self.init_logger()

        self.pid_to_kill = pid_to_kill
        self.async_loop = async_loop

        self.sleep_interval = sleep_interval
        self.time_elapsed = 0.0

        self.soft_timeout = soft_timeout
        self.hard_timeout = hard_timeout
        self.critical_timeout = critical_timeout

        self.soft_timeout_raised = False
        self.hard_timeout_raised = False
        self.critical_timeout_raised = False

        self.running = False

        self.async_loop.create_task(self.kill_loop())

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
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(
            fmt=logging.Formatter(
                fmt='%(asctime)s %(name)-12s %(process)d %(levelname)-8s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
            ),
        )
        self.logger.addHandler(
            hdlr=stream_handler,
        )

    def datagram_received(
        self,
        data: bytes,
        addr: typing.Tuple[str, int],
    ) -> None:
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

    async def kill_loop(
        self,
    ) -> None:
        self.logger.info(
            msg='kill loop started',
        )

        process_to_kill = psutil.Process(
            pid=self.pid_to_kill,
        )
        while self.is_process_alive(
            process=process_to_kill,
        ):
            if self.running:
                self.check_and_process_soft_timeout()
                self.check_and_process_hard_timeout()
                self.check_and_process_critical_timeout()

                self.time_elapsed += self.sleep_interval

            await asyncio.sleep(
                delay=self.sleep_interval,
                loop=self.async_loop,
            )

        self.kill_process(
            pid=process_to_kill.pid,
            signal=signal.SIGTERM,
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
            self.logger.error(
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
                pid=self.pid_to_kill,
                signal=signal.SIGINT,
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
                pid=self.pid_to_kill,
                signal=signal.SIGABRT,
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
                pid=self.pid_to_kill,
                signal=signal.SIGTERM,
            )

    def kill_process(
        self,
        pid: int,
        signal: int,
    ) -> None:
        try:
            self.logger.info(
                msg='kill_process request',
            )

            os.kill(pid, signal)
        except Exception as exception:
            self.logger.error(
                msg=str(exception),
            )


class Killer:
    def __init__(
        self,
        pid_to_kill: int,
        sleep_interval: float,
        soft_timeout: float,
        hard_timeout: float,
        critical_timeout: float,
    ) -> None:
        parent_pipe, child_pipe = multiprocessing.Pipe()

        self.killer_process = subprocess.Popen(
            args=shlex.split(
                s=(
                    f'{sys.executable} -m {__name__} '
                    f'--pid-to-kill {pid_to_kill} '
                    f'--sleep-interval {sleep_interval} '
                    f'--soft-timeout {soft_timeout} '
                    f'--hard-timeout {hard_timeout} '
                    f'--critical-timeout {critical_timeout} '
                    f'--pipe-fd {child_pipe.fileno()} '
                ),
            ),
            stderr=subprocess.DEVNULL,
            pass_fds=[
                child_pipe.fileno(),
            ],
        )

        port = parent_pipe.recv()

        self.killer_socket = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_DGRAM,
        )
        self.killer_socket.connect(
            (
                'localhost',
                port,
            )
        )

        parent_pipe.close()
        child_pipe.close()

    def start(
        self,
    ) -> None:
        self.killer_socket.send(b'start')

    def stop(
        self,
    ) -> None:
        self.killer_socket.send(b'stop')

    def reset(
        self,
    ) -> None:
        self.killer_socket.send(b'reset')

    def stop_and_reset(
        self,
    ) -> None:
        self.killer_socket.send(b'stop_and_reset')

    def kill(
        self,
    ) -> None:
        try:
            self.killer_socket.close()
        except Exception:
            pass

        try:
            self.killer_process.terminate()
        except Exception:
            pass

        try:
            self.killer_process.wait()
        except (
            ChildProcessError,
            OSError,
        ):
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

    server_socket = socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_DGRAM,
    )
    server_socket.bind(
        (
            'localhost',
            0,
        ),
    )
    server_socket_host, server_socket_port = server_socket.getsockname()

    pipe = multiprocessing.connection.Connection(
        handle=args.pipe_fd,
    )
    pipe.send(
        obj=server_socket_port,
    )
    pipe.close()

    async_loop = asyncio.new_event_loop()
    killer_udp_server_endpoint = async_loop.create_datagram_endpoint(
        protocol_factory=lambda: KillerServer(
            async_loop=async_loop,
            pid_to_kill=args.pid_to_kill,
            sleep_interval=args.sleep_interval,
            soft_timeout=args.soft_timeout,
            hard_timeout=args.hard_timeout,
            critical_timeout=args.critical_timeout,
        ),
        sock=server_socket,
    )
    async_loop.create_task(killer_udp_server_endpoint)

    try:
        async_loop.run_forever()
    except Exception:
        async_loop.close()


if __name__ == '__main__':
    main()
