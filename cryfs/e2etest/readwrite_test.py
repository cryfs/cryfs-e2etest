import pkg_resources
import asyncio
import attr
import shutil
import tempfile
import os
from cryfs.e2etest.utils.tar import TarFile, TarUnpacker
from cryfs.e2etest.fsmounter import IFsMounter
from cryfs.e2etest.utils.status import TestStatus, TestResult, TestResults, merge_results
from cryfs.e2etest.utils.logger import Logger, LogLevel
from cryfs.e2etest.utils.dircomp import dir_equals


class Fixture(object):
    def __init__(self, data: str) -> None:
        data_file = pkg_resources.resource_filename(__name__, data)
        self._data = data
        self._data_tar = TarFile(data_file)

    def unpack_data(self) -> TarUnpacker:
        return TarUnpacker(self._data_tar)

    async def unpack_data_to(self, dest_path: str) -> None:
        await self._data_tar.unpack(dest_path)

    def name(self) -> str:
        return self._data


fixtures = [Fixture(
    data="fixtures/scrypt_data.tar",
)]


class ReadWriteTests(object):
    def __init__(self, mounter: IFsMounter) -> None:
        self.mounter = mounter

    async def run(self) -> TestResults:
        results = await asyncio.gather(*[self._test(fixture) for fixture in fixtures])
        return merge_results(results)

    async def _test(self, fixture: Fixture) -> TestResults:
        results = await asyncio.gather(
            self._test_copy_and_read(fixture),
            self._test_untar_and_read(fixture),
        )
        return TestResults(list(results))

    async def _test_copy_and_read(self, fixture: Fixture) -> TestResult:
        logger = Logger()
        password = b"mypassword"
        try:
            with tempfile.TemporaryDirectory() as basedir:
                async with fixture.unpack_data() as datadir:
                    async with self.mounter.mount(basedir, password, logger) as mountdir:
                        _mountdir = os.path.join(mountdir, 'contents')
                        shutil.copytree(datadir, _mountdir, symlinks=True)
                        if not dir_equals(datadir, _mountdir, logger):
                            logger.log(LogLevel.ERROR, "Directories %s and %s aren't equal" % (datadir, mountdir))
                    # unmount and remount, then test again
                    async with self.mounter.mount(basedir, password, logger) as mountdir:
                        _mountdir = os.path.join(mountdir, 'contents')
                        if not dir_equals(datadir, _mountdir, logger):
                            logger.log(LogLevel.ERROR, "Directories %s and %s aren't equal" % (datadir, mountdir))
            # Unroll the with statements before returning because they might add something to the logger
            return TestResult(fixture_name="ReadWriteTest.copy_and_read: %s" % fixture.name(), log=logger)
        except Exception as e:
            logger.log(LogLevel.FATAL, "Exception: " + str(e))
            return TestResult(fixture_name="ReadWriteTest.copy_and_read: %s" % fixture.name(), log=logger)

    async def _test_untar_and_read(self, fixture: Fixture) -> TestResult:
        logger = Logger()
        password = b"mypassword"
        try:
            with tempfile.TemporaryDirectory() as basedir:
                async with fixture.unpack_data() as datadir:
                    async with self.mounter.mount(basedir, password, logger) as mountdir:
                        await fixture.unpack_data_to(mountdir)
                        if not dir_equals(datadir, mountdir, logger):
                            logger.log(LogLevel.ERROR, "Directories %s and %s aren't equal" % (datadir, mountdir))
                    # unmount and remount, then test again
                    async with self.mounter.mount(basedir, password, logger) as mountdir:
                        if not dir_equals(datadir, mountdir, logger):
                            logger.log(LogLevel.ERROR, "Directories %s and %s aren't equal" % (datadir, mountdir))
            # Unroll the with statements before returning because they might add something to the logger
            return TestResult(fixture_name="ReadWriteTest.untar_and_read: %s" % fixture.name(), log=logger)
        except Exception as e:
            logger.log(LogLevel.FATAL, "Exception: " + str(e))
            return TestResult(fixture_name="ReadWriteTest.untar_and_read: %s" % fixture.name(), log=logger)
