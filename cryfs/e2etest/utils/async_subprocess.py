from asyncio import subprocess, create_subprocess_exec
from typing import Any, Optional
from cryfs.e2etest.utils.logger import Logger, LogLevel
import attr


class SubprocessException(Exception):
    def __init__(self, message: str) -> None:
        self._message = message

    def message(self) -> str:
        return self._message


@attr.s(auto_attribs=True)
class CallResult(object):
    stdout: bytes
    stderr: bytes


async def check_call_subprocess(*args: Any, input: Optional[bytes] = None, stdout: int = subprocess.PIPE, logger: Optional[Logger] = None, throw_on_error: bool = True, **kwargs: Any) -> CallResult:
    process = await create_subprocess_exec(*args, stdin=subprocess.PIPE, stdout=stdout,
                                           stderr=subprocess.PIPE, **kwargs)
    (stdout_data, stderr_data) = await process.communicate(input)
    if process.returncode != 0:
        stderr = stderr_data.decode(encoding="UTF-8")
        if logger is not None:
            logger.log(LogLevel.FATAL, "Process stderr: %s" % stderr)
        if throw_on_error:
            raise SubprocessException(stderr)
    return CallResult(stdout=stdout_data, stderr=stderr_data)
