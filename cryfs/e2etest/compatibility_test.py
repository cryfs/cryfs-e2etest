# Test that the current version of CryFS can still load old versions

from cryfs.e2etest.fixture import Fixture
import asyncio
import attr
from enum import Enum
from cryfs.e2etest.utils.dircomp import dir_equals
from cryfs.e2etest.fsmounter import IFsMounter
from cryfs.e2etest.utils.logger import Logger, LogLevel

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


class TestStatus(Enum):
    SUCCESS = 1
    ERROR = 2
    FATAL = 3

    def to_string(self) -> str:
        return {
            TestStatus.SUCCESS: "SUCCESS",
            TestStatus.ERROR: "ERROR",
            TestStatus.FATAL: "FATAL",
        }[self]


@attr.s(auto_attribs=True)
class TestResult(object):
    fixture: Fixture
    log: Logger

    def status(self) -> TestStatus:
        if self.log.contains_entry_with_level(LogLevel.FATAL):
            return TestStatus.FATAL
        elif self.log.contains_entry_with_level(LogLevel.ERROR):
            return TestStatus.ERROR
        else:
            return TestStatus.SUCCESS


class CompatibilityTests(object):
    def __init__(self, mounter: IFsMounter) -> None:
        self.mounter = mounter

    async def run(self) -> TestStatus:
        results = await asyncio.gather(*[self.test_reads_correctly(fixture) for fixture in fixtures])
        for result in results:
            print("[%s] %s" % (result.status().to_string(), result.fixture.name()))
        fatalled = [r for r in results if r.status() == TestStatus.FATAL]
        errored = [r for r in results if r.status() == TestStatus.ERROR]
        for result in fatalled:
            self._print_result(result)
        for result in errored:
            self._print_result(result)
        if len(fatalled) != 0:
            return TestStatus.FATAL
        elif len(errored) != 0:
            return TestStatus.ERROR
        else:
            return TestStatus.SUCCESS

    async def test_reads_correctly(self, fixture: Fixture) -> TestResult:
        logger = Logger()
        try:
            async with fixture.unpack_encoded() as basedir, fixture.unpack_data() as datadir:
                async with self.mounter.mount(basedir, fixture.password(), logger) as mountdir:
                    if not dir_equals(datadir, mountdir, logger):
                        logger.log(LogLevel.ERROR, "Directories %s and %s aren't equal" % (datadir, mountdir))
            # Unroll the with statements before returning because they might add something to the logger
            return TestResult(fixture=fixture, log=logger)
        except Exception as e:
            logger.log(LogLevel.FATAL, "Exception: " + str(e))
            return TestResult(fixture=fixture, log=logger)

    def _print_result(self, result: TestResult) -> None:
        print("-------------------------")
        print("Detailed result for [%s] %s" % (result.status().to_string(), result.fixture.name()))
        print("-------------------------")
        print(result.log.to_string())
        print()
