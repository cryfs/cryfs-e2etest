from asyncio import subprocess, create_subprocess_exec
from typing import Any, Optional


class SubprocessException(Exception):
    def __init__(self, message: str) -> None:
        self._message = message

    def message(self) -> str:
        return self._message


async def check_call_subprocess(*args: Any, input: Optional[bytes] = None, stdout: int = subprocess.PIPE, **kwargs: Any) -> bytes:
    process = await create_subprocess_exec(*args, stdin=subprocess.PIPE, stdout=stdout,
                                           stderr=subprocess.PIPE, **kwargs)
    (stdout_data, stderr_data) = await process.communicate(input)
    if process.returncode != 0:
        raise SubprocessException(stderr_data.decode(encoding="UTF-8"))
    return stdout_data
