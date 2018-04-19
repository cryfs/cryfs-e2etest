# Test that the current version of CryFS can still load old versions

from typing import List
import pkg_resources
from cryfs.e2etest.test_framework.dircomp import expect_dir_equals
from cryfs.e2etest.fsmounter import IFsMounter
from cryfs.e2etest.test_framework.logger import Logger
from cryfs.e2etest.utils.tar import TarFile, TarUnpacker
from cryfs.e2etest.test_framework.test_case import ITestSuite, ITestCase


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
    password=b"mypassword",
), Fixture(
    data="fixtures/scrypt_data.tar",
    encoded="fixtures/scrypt_cryfs0.9.7_encoded.tar",
    password=b"mypassword",
), Fixture(
    data="fixtures/scrypt_data.tar",
    encoded="fixtures/scrypt_cryfs0.9.8_encoded.tar",
    password=b"mypassword",
), Fixture(
    data="fixtures/scrypt_data.tar",
    encoded="fixtures/scrypt_cryfs0.9.9_encoded.tar",
    password=b"mypassword",
), Fixture(
    data="fixtures/scrypt_data.tar",
    encoded="fixtures/scrypt_cryfs0.10-m2+188.gfc71242e_encoded.tar",
    password=b"mypassword",
), Fixture(
    data="fixtures/constructed_data.tar",
    encoded="fixtures/constructed_cryfs0.9.6_encoded.tar",
    password=b"mypassword",
), Fixture(
    data="fixtures/constructed_data.tar",
    encoded="fixtures/constructed_cryfs0.9.7_encoded.tar",
    password=b"mypassword",
), Fixture(
    data="fixtures/constructed_data.tar",
    encoded="fixtures/constructed_cryfs0.9.8_encoded.tar",
    password=b"mypassword",
), Fixture(
    data="fixtures/constructed_data.tar",
    encoded="fixtures/constructed_cryfs0.9.9_encoded.tar",
    password=b"mypassword",
), Fixture(
    data="fixtures/constructed_data.tar",
    encoded="fixtures/constructed_cryfs0.10-m2+194.gb0077e7a_encoded.tar",
    password=b"mypassword",
)]


class CompatibilityTests(ITestSuite):
    def __init__(self, mounter: IFsMounter) -> None:
        self.mounter = mounter

    class _CompatibilityTest(ITestCase):
        def __init__(self, fixture: Fixture, mounter: IFsMounter) -> None:
            self.fixture = fixture
            self.mounter = mounter

        async def run(self, logger: Logger) -> None:
            async with self.fixture.unpack_encoded() as basedir, self.fixture.unpack_data() as datadir:
                async with self.mounter.mount(basedir, self.fixture.password(), logger) as mountdir:
                    expect_dir_equals(datadir, mountdir, logger)

        def name(self) -> str:
            return "CompatibilityTest: %s" % self.fixture.name()

    def test_cases(self) -> List[ITestCase]:
        return [self._CompatibilityTest(fixture, self.mounter) for fixture in fixtures]
