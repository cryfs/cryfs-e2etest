import pkg_resources
import shutil
import tempfile
import os
from typing import List
from cryfs.e2etest.utils.tar import TarFile, TarUnpacker
from cryfs.e2etest.fsmounter import IFsMounter
from cryfs.e2etest.test_framework.test_case import ITestSuite, ITestCase
from cryfs.e2etest.test_framework.logger import Logger
from cryfs.e2etest.test_framework.dircomp import expect_dir_equals


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


class ReadWriteTests(ITestSuite):
    def __init__(self, mounter: IFsMounter) -> None:
        self.mounter = mounter

    class _CopyAndReadTest(ITestCase):
        def __init__(self, fixture: Fixture, mounter: IFsMounter) -> None:
            self.fixture = fixture
            self.mounter = mounter

        async def run(self, logger: Logger) -> None:
            password = b"mypassword"
            with tempfile.TemporaryDirectory() as basedir:
                async with self.fixture.unpack_data() as datadir:
                    async with self.mounter.mount(basedir, password, logger) as mountdir:
                        _mountdir = os.path.join(mountdir, 'contents')
                        shutil.copytree(datadir, _mountdir, symlinks=True)
                        expect_dir_equals(datadir, _mountdir, logger)
                    # unmount and remount, then test again
                    async with self.mounter.mount(basedir, password, logger) as mountdir:
                        _mountdir = os.path.join(mountdir, 'contents')
                        expect_dir_equals(datadir, _mountdir, logger)

        def name(self) -> str:
            return "ReadWriteTest.copy_and_read: %s" % self.fixture.name()

    class _UntarAndReadTest(ITestCase):
        def __init__(self, fixture: Fixture, mounter: IFsMounter) -> None:
            self.fixture = fixture
            self.mounter = mounter

        async def run(self, logger: Logger) -> None:
            password = b"mypassword"
            with tempfile.TemporaryDirectory() as basedir:
                async with self.fixture.unpack_data() as datadir:
                    async with self.mounter.mount(basedir, password, logger) as mountdir:
                        await self.fixture.unpack_data_to(mountdir)
                        expect_dir_equals(datadir, mountdir, logger)
                    # unmount and remount, then test again
                    async with self.mounter.mount(basedir, password, logger) as mountdir:
                        expect_dir_equals(datadir, mountdir, logger)

        def name(self) -> str:
            return "ReadWriteTest.untar_and_read: %s" % self.fixture.name()

    def test_cases(self) -> List[ITestCase]:
        result: List[ITestCase] = []
        result += [self._CopyAndReadTest(fixture, self.mounter) for fixture in fixtures]
        result += [self._UntarAndReadTest(fixture, self.mounter) for fixture in fixtures]
        return result
