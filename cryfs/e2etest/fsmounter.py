from typing import Optional
import tempfile
from abc import ABCMeta, abstractmethod
from types import TracebackType
from cryfs.e2etest.utils.async_subprocess import check_call_subprocess
from cryfs.e2etest.test_framework.logger import Logger, LogLevel
import asyncio


class _IMounterContext(object, metaclass=ABCMeta):
    async def __aenter__(self) -> str: ...
    async def __aexit__(self, exc_type: Optional[type], exc: Optional[BaseException], tb: Optional[TracebackType]) -> None: ...


class IFsMounter(object, metaclass=ABCMeta):
    @abstractmethod
    def mount(self, basedir: str, password: bytes, logger: Optional[Logger] = None) -> _IMounterContext: ...


class _CryfsMounterContext(_IMounterContext):
    def __init__(self, cryfs_binary: str, basedir: str, password: bytes, logger: Optional[Logger] = None) -> None:
        self.cryfs_binary = cryfs_binary
        self.basedir = basedir
        self.password = password
        self.logger = logger

    async def __aenter__(self) -> str:
        self.temp_local_state_dir = tempfile.TemporaryDirectory()
        self.temp_basedir = tempfile.TemporaryDirectory()
        self.logfile = tempfile.NamedTemporaryFile()
        out = await check_call_subprocess(self.cryfs_binary, self.basedir, self.temp_basedir.name,
                                          "--allow-filesystem-upgrade", "--logfile", self.logfile.name,
                                          input=self.password, env={
            "CRYFS_FRONTEND": "noninteractive",
            "CRYFS_NO_UPDATE_CHECK": "true",
            "CRYFS_LOCAL_STATE_DIR": self.temp_local_state_dir.name,
        })
        if self.logger is not None:
            self.logger.log(LogLevel.INFO, "CryFS stdout:\n%s" % out.stdout.decode('UTF-8'))
            self.logger.log(LogLevel.INFO, "CryFS stderr:\n%s" % out.stderr.decode('UTF-8'))

        return self.temp_basedir.name

    async def __aexit__(self, exc_type: Optional[type], exc: Optional[BaseException], tb: Optional[TracebackType]) -> None:
        await check_call_subprocess("/bin/fusermount", "-u", self.temp_basedir.name, logger=self.logger, throw_on_error=False)
        await _wait_until_unmounted(self.temp_basedir.name)
        if self.logger is not None:
            with open(self.logfile.name, 'r') as logfile:
                self.logger.log(LogLevel.INFO, "CryFS log:\n%s" % logfile.read())
        self.temp_basedir.cleanup()
        self.temp_local_state_dir.cleanup()
        self.logfile.close()


class CryfsMounter(IFsMounter):
    def __init__(self, cryfs_binary: str) -> None:
        self.cryfs_binary = cryfs_binary

    def mount(self, basedir: str, password: bytes, logger: Optional[Logger] = None) -> _CryfsMounterContext:
        return _CryfsMounterContext(cryfs_binary=self.cryfs_binary, basedir=basedir, password=password, logger=logger)


async def _wait_until_unmounted(dir: str) -> None:
    mounted_dirs = await check_call_subprocess("mount")
    while dir.encode("UTF-8") in mounted_dirs.stdout:
        await asyncio.sleep(0.001)
    # Give the cryfs process some more time to exit and finish writing to the basedir
    await asyncio.sleep(5)
