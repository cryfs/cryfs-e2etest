# Test that the current version of CryFS can still load old versions

import asyncio
import attr
import pkg_resources
from cryfs.e2etest.utils.status import TestStatus, TestResult, TestResults
from cryfs.e2etest.utils.dircomp import dir_equals
from cryfs.e2etest.fsmounter import IFsMounter
from cryfs.e2etest.utils.logger import Logger, LogLevel
from cryfs.e2etest.utils.tar import TarFile, TarUnpacker


class Fixture(object):
    def __init__(self, data: str, encoded: str, password: bytes) -> None:
        data_file = pkg_resources.resource_filename(__name__, data)
        encoded_file = pkg_resources.resource_filename(__name__, encoded)
        self._data = data
        self._encoded = encoded
        self._data_tar = TarFile(data_file)
        self._encoded_tar = TarFile(encoded_file)
        self._password = password

    def unpack_data(self) -> TarUnpacker:
        return TarUnpacker(self._data_tar)

    def unpack_encoded(self) -> TarUnpacker:
        return TarUnpacker(self._encoded_tar)

    def password(self) -> bytes:
        return self._password

    def name(self) -> str:
        return self._data + " : " + self._encoded


fixtures = [Fixture(
    data="fixtures/scrypt_data.tar",
    encoded="fixtures/scrypt_cryfs0.9.6_encoded.tar",
    password=b"mypassword"
), Fixture(
    data="fixtures/scrypt_data.tar",
    encoded="fixtures/scrypt_cryfs0.9.7_encoded.tar",
    password=b"mypassword"
), Fixture(
    data="fixtures/scrypt_data.tar",
    encoded="fixtures/scrypt_cryfs0.9.8_encoded.tar",
    password=b"mypassword"
), Fixture(
    data="fixtures/scrypt_data.tar",
    encoded="fixtures/scrypt_cryfs0.9.9_encoded.tar",
    password=b"mypassword"
), Fixture(
    data="fixtures/scrypt_data.tar",
    encoded="fixtures/scrypt_cryfs0.10-m2+188.gfc71242e_encoded.tar",
    password=b"mypassword"
)]


class CompatibilityTests(object):
    def __init__(self, mounter: IFsMounter) -> None:
        self.mounter = mounter

    async def run(self) -> TestResults:
        results = await asyncio.gather(*[self._test(fixture) for fixture in fixtures])
        return TestResults(results)

    async def _test(self, fixture: Fixture) -> TestResult:
        logger = Logger()
        try:
            async with fixture.unpack_encoded() as basedir, fixture.unpack_data() as datadir:
                async with self.mounter.mount(basedir, fixture.password(), logger) as mountdir:
                    if not dir_equals(datadir, mountdir, logger):
                        logger.log(LogLevel.ERROR, "Directories %s and %s aren't equal" % (datadir, mountdir))
            # Unroll the with statements before returning because they might add something to the logger
            return TestResult(fixture_name="CompatibilityTest: %s" % fixture.name(), log=logger)
        except Exception as e:
            logger.log(LogLevel.FATAL, "Exception: " + str(e))
            return TestResult(fixture_name="CompatibilityTest: %s" % fixture.name(), log=logger)
