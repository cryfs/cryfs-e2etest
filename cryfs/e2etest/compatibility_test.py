# Test that the current version of CryFS can still load old versions

from cryfs.e2etest.fixture import Fixture
import asyncio
from cryfs.e2etest.utils.dircomp import dir_equals
from cryfs.e2etest.fsmounter import IFsMounter

fixtures = [Fixture(
    data="fixtures/scrypt_data.tar",
    encoded="fixtures/scrypt_cryfs0.9.8_encoded.tar",
    password=b"mypassword"
)]


class CompatibilityTests(object):
    def __init__(self, mounter: IFsMounter) -> None:
        self.mounter = mounter

    async def run(self) -> None:
        await asyncio.gather(*[self.test_reads_correctly(fixture) for fixture in fixtures])

    async def test_reads_correctly(self, fixture: Fixture) -> None:
        async with fixture.unpack_encoded() as basedir, fixture.unpack_data() as datadir:
            async with self.mounter.mount(basedir, fixture.password()) as mountdir:
                if not dir_equals(datadir, mountdir):
                    print("Directories %s and %s aren't equal" % (datadir, mountdir))
                    # TODO Instead of exit(1), we should accumulate errors and show at the end
                    exit(1)
