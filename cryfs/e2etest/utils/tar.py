from typing import Optional
from types import TracebackType
import tempfile
from cryfs.e2etest.utils.async_subprocess import check_call_subprocess


class TarFile(object):
    def __init__(self, tar_path: str) -> None:
        self.tar_path = tar_path

    async def unpack(self, dest_path: str) -> None:
        # Use --same-owner, but that needs sudo
        await check_call_subprocess("tar", "--preserve-permissions", "--atime-preserve", "-C", dest_path, "-xvf", self.tar_path)


class TarUnpacker(object):
    def __init__(self, tar_file: TarFile) -> None:
        self.tar_file = tar_file

    async def __aenter__(self) -> str:
        self.tempdir = tempfile.TemporaryDirectory()
        await self.tar_file.unpack(self.tempdir.name)
        return self.tempdir.name

    async def __aexit__(self, exc_type: Optional[type], exc: Optional[BaseException], tb: Optional[TracebackType]) -> None:
        self.tempdir.cleanup()
