from typing import Optional
import tempfile
from abc import ABCMeta, abstractmethod
from types import TracebackType
from cryfs.e2etest.utils.async_subprocess import check_call_subprocess
from asyncio import subprocess


class _IMounterContext(object, metaclass=ABCMeta):
    async def __aenter__(self) -> str: ...
    async def __aexit__(self, exc_type: Optional[type], exc: Optional[BaseException], tb: Optional[TracebackType]) -> None: ...


class IFsMounter(object, metaclass=ABCMeta):
    @abstractmethod
    def mount(self, basedir: str, password: bytes) -> _IMounterContext: ...


class _CryfsMounterContext(_IMounterContext):
    def __init__(self, cryfs_binary: str, basedir: str, password: bytes) -> None:
        self.cryfs_binary = cryfs_binary
        self.basedir = basedir
        self.password = password

    async def __aenter__(self) -> str:
        self.tempdir = tempfile.TemporaryDirectory()
        out = await check_call_subprocess(self.cryfs_binary, self.basedir, self.tempdir.name, "--allow-filesystem-upgrade",
                                    input=self.password, env={
            "CRYFS_FRONTEND": "noninteractive",
            "CRYFS_NO_UPDATE_CHECK": "true"
        })

        return self.tempdir.name

    async def __aexit__(self, exc_type: Optional[type], exc: Optional[BaseException], tb: Optional[TracebackType]) -> None:
        await check_call_subprocess("/bin/fusermount", "-u", self.tempdir.name)
        self.tempdir.cleanup()


class CryfsMounter(IFsMounter):
    def __init__(self, cryfs_binary: str) -> None:
        self.cryfs_binary = cryfs_binary

    def mount(self, basedir: str, password: bytes) -> _CryfsMounterContext:
        return _CryfsMounterContext(cryfs_binary=self.cryfs_binary, basedir=basedir, password=password)
