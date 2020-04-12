import os
import signal
import asyncio
import subprocess
import shlex
import sys
import psutil
import argparse
import socket
import logging

from .. import logger


class ProcessKillerServer(
    asyncio.DatagramProtocol,
):
    def __init__(
        self,
        async_loop,
        pid_to_kill,
        sleep_interval,
        soft_timeout,
        hard_timeout,
        critical_timeout,
    ):
        super().__init__()

        self.logger = logger.logger.Logger(
            logger_name='Killer',
            log_level=logging.ERROR,
            log_to_stdout=True,
        )

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

        self.soft_timeout_signal = signal.SIGINT
        self.hard_timeout_signal = signal.SIGABRT
        self.critical_timeout_signal = signal.SIGTERM

        self.running = False

        self.initialized = False

    def connection_made(
        self,
        transport,
    ):
        self.transport = transport

        udp_port = self.transport._sock.getsockname()[1]
        sys.stdout.write(str(udp_port) + '\n')
        sys.stdout.flush()

    def datagram_received(
        self,
        data,
        addr,
    ):
        if data == b'start':
            self.logger.info(
                msg='start request was received',
            )
            if not self.initialized:
                self.async_loop.create_task(self.kill_loop())
                self.initialized = True

            self.killer_start()
        elif data == b'stop':
            self.logger.info(
                msg='stop request was received',
            )
            self.killer_stop()
        elif data == b'reset':
            self.logger.info(
                msg='reset request was received',
            )
            self.killer_reset()
        elif data == b'stop_and_reset':
            self.logger.info(
                msg='stop_and_reset request was received',
            )
            self.killer_stop()
            self.killer_reset()

    async def kill_loop(
        self,
    ):
        self.logger.info(
            msg='kill loop started',
        )

        while True:
            try:
                if not psutil.pid_exists(
                    pid=self.pid_to_kill,
                ):
                    self.logger.info(
                        msg='pid does not exist anymore, exiting',
                    )

                    os.kill(os.getpid(), 9)

                pid_to_kill_process = psutil.Process(
                    pid=self.pid_to_kill,
                )
                pid_to_kill_process_status = pid_to_kill_process.status()
                if pid_to_kill_process_status in [
                    psutil.STATUS_DEAD,
                    psutil.STATUS_ZOMBIE,
                ]:
                    self.logger.error(
                        msg=f'kill_loop process status not running: {pid_to_kill_process_status}',
                    )
                    os.kill(os.getpid(), 9)

                if self.running:
                    if not self.soft_timeout_raised and self.soft_timeout != 0 and self.time_elapsed >= self.soft_timeout:
                        self.logger.info(
                            msg='raising soft timeout',
                        )
                        self.soft_timeout_raised = True
                        self.kill_process(
                            pid=self.pid_to_kill,
                            signal=self.soft_timeout_signal,
                        )

                    if not self.hard_timeout_raised and self.hard_timeout != 0 and self.time_elapsed >= self.hard_timeout:
                        self.logger.info(
                            msg='raising hard timeout',
                        )
                        self.hard_timeout_raised = True
                        self.kill_process(
                            pid=self.pid_to_kill,
                            signal=self.hard_timeout_signal,
                        )

                    if not self.critical_timeout_raised and self.critical_timeout != 0 and self.time_elapsed >= self.critical_timeout:
                        self.logger.info(
                            msg='raising critical timeout',
                        )
                        self.critical_timeout_raised = True
                        self.kill_process(
                            pid=self.pid_to_kill,
                            signal=self.critical_timeout_signal,
                        )

                    self.time_elapsed += self.sleep_interval

                await asyncio.sleep(
                    delay=self.sleep_interval,
                    loop=self.async_loop,
                )
            except Exception as exception:
                self.logger.error(
                    msg=f'kill_loop exception occured: {exception}',
                )

    def kill_process(
        self,
        pid,
        signal,
    ):
        try:
            self.logger.info(
                msg='kill_process request',
            )

            os.kill(pid, signal)
        except Exception as exception:
            self.logger.error(
                msg=str(exception),
            )

    def killer_start(
        self,
    ):
        self.running = True

        self.logger.info(
            msg='started',
        )

    def killer_stop(
        self,
    ):
        self.running = False

        self.logger.info(
            msg='stopped',
        )

    def killer_reset(
        self,
    ):
        self.time_elapsed = 0.0
        self.soft_timeout_raised = False
        self.hard_timeout_raised = False
        self.critical_timeout_raised = False

        self.logger.info(
            msg='reset',
        )


class ProcessKiller:
    def __init__(
        self,
        pid_to_kill,
        sleep_interval,
        soft_timeout,
        hard_timeout,
        critical_timeout,
    ):
        self.killer_process = subprocess.Popen(
            args=shlex.split(
                s=f'python3 -m {__name__} --pid-to-kill {pid_to_kill} --sleep-interval {sleep_interval} --soft-timeout {soft_timeout} --hard-timeout {hard_timeout} --critical-timeout {critical_timeout}',
            ),
            cwd=os.path.join(
                os.path.dirname(
                    p=os.path.realpath(
                        filename=__file__,
                    ),
                ),
                '../../'
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=1,
            universal_newlines=True,
        )

        self.port = int(self.killer_process.stdout.readline().strip())
        self.killer_process.stdout.close()

        self.killer_socket = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_DGRAM,
        )
        self.address = (
            '127.0.0.1',
            self.port,
        )
        self.killer_socket.connect(self.address)

    def start(
        self,
    ):
        self.killer_socket.send(b'start')

    def stop(
        self,
    ):
        self.killer_socket.send(b'stop')

    def reset(
        self,
    ):
        self.killer_socket.send(b'reset')

    def stop_and_reset(
        self,
    ):
        self.killer_socket.send(b'stop_and_reset')

    def kill(
        self,
    ):
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
    ):
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

    args = parser.parse_args()

    async_loop = asyncio.new_event_loop()

    killer_udp_server_endpoint = async_loop.create_datagram_endpoint(
        protocol_factory=lambda: ProcessKillerServer(
            async_loop=async_loop,
            pid_to_kill=args.pid_to_kill,
            sleep_interval=args.sleep_interval,
            soft_timeout=args.soft_timeout,
            hard_timeout=args.hard_timeout,
            critical_timeout=args.critical_timeout,
        ),
        local_addr=(
            '127.0.0.1',
            0,
        ),
    )

    async_loop.create_task(killer_udp_server_endpoint)

    try:
        async_loop.run_forever()
    except Exception:
        async_loop.close()


if __name__ == '__main__':
    main()
