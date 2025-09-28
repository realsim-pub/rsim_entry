#!/usr/bin python
# -*- coding: UTF-8 -*-
import os
import fcntl
import time
import signal
import select
import subprocess
from third_party.python.common.logger.logger import Logger

logger = Logger.get_logger(__name__)


class ShellRun(object):
    @staticmethod
    def async_run(cmd):
        ps = None
        code = 0
        message = ""
        logger.info(cmd)
        try:
            ps = subprocess.Popen(
                cmd,
                shell=True,
                executable="bash",
                stdout=None,
                stderr=None,
                preexec_fn=os.setsid,
            )
        except Exception as error:
            code = -1
            message = str(error)
        return code, message, ps

    @staticmethod
    def sync_run(cmd, timeout=None, print_log=False, need_msg=True):
        ps = None
        code = 0
        message = ""
        start_time = time.time()

        try:
            ps = subprocess.Popen(
                cmd,
                shell=True,
                executable="bash",
                stdout=subprocess.PIPE if need_msg else None,
                stderr=subprocess.PIPE if need_msg else None,
                preexec_fn=os.setsid,
            )

            err_log = ""
            out_log = ""
            err = ps.stderr
            out = ps.stdout

            if need_msg:
                flags = fcntl.fcntl(err, fcntl.F_GETFL)
                fcntl.fcntl(out, fcntl.F_SETFL, flags | os.O_NONBLOCK)
                flags = fcntl.fcntl(err, fcntl.F_GETFL)
                fcntl.fcntl(err, fcntl.F_SETFL, flags | os.O_NONBLOCK)

            def read_output(fd):
                output = fd.read().rstrip().decode()
                if len(output) > 0:
                    if print_log:
                        logger.info(output)
                    return output
                else:
                    return ""

            while True:
                if timeout:
                    if (time.time() - start_time) > timeout:
                        os.killpg(os.getpgid(ps.pid), signal.SIGTERM)
                        os.kill(ps.pid, signal.SIGTERM)
                        ps.wait(timeout=2)
                        code = -1
                        message = f"run timeout:  {(time.time() - start_time)}s"
                        break

                status = ps.poll()
                if status is None:
                    if not need_msg:
                        time.sleep(0.1)
                        continue
                    result = select.select([err, out], [], [])[0]

                    if len(result) == 0:
                        time.sleep(0.1)
                        continue
                    elif len(result) > 0:
                        for item in result:
                            if item == out:
                                out_log = read_output(item)
                            elif item == err:
                                err_log += read_output(item)
                                if len(err_log) > 10000:
                                    err_log = err_log[-8000:]
                else:
                    code = status
                    if err_log:
                        message = err_log
                    elif need_msg:
                        message = read_output(err)
                    break
            ps.wait()
        except Exception as error:
            code = -1
            message = str(error)
        return code, message, ps

    @staticmethod
    def run_cmd_with_output(cmd, timeout=None):
        end_time = time.time()
        if timeout:
            end_time = time.time() + timeout

        res = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=True,
        )
        while True:
            if res.poll() is not None:
                break

            time.sleep(0.1)
            if timeout:
                if end_time <= time.time():
                    out = res.stdout.readlines()
                    err = res.stderr.readlines()
                    res.kill()
                    return [out], ["TIMEOUT {}, error:{}".format(timeout, err)]

        out = res.stdout.readlines()
        format_out = []
        for item in out:
            format_out.append(str(item.decode()).strip("\n"))
        err = res.stderr.readlines()
        return format_out, err
