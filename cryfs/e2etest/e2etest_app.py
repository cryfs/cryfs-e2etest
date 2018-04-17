import sys
import traceback as _traceback
from typing import List, Type, TypeVar, Optional
import asyncio
from types import TracebackType
from cryfs.e2etest.fsmounter import CryfsMounter
from cryfs.e2etest.utils.async_app import AsyncApp
from cryfs.e2etest.utils.status import TestStatus, merge_results
from cryfs.e2etest.compatibility_test import CompatibilityTests
from cryfs.e2etest.readwrite_test import ReadWriteTests


T = TypeVar('T')


class Application(AsyncApp):
    def __init__(self, argv: List[str]) -> None:
        self.argv = argv

    # TODO Auto-call this in run()
    def setupUncaughtExceptionHandler(self) -> None:
        sys.excepthook = self._onUncaughtException

    async def main(self) -> None:
        mounter = CryfsMounter("/usr/local/bin/cryfs")
        results = await asyncio.gather(
            CompatibilityTests(mounter).run(),
            ReadWriteTests(mounter).run(),
        )
        result = merge_results(results)
        result.print()
        if result.status() != TestStatus.SUCCESS:
            exit(1)

    def _onUncaughtException(self, type_: Type[BaseException], value: BaseException, traceback: TracebackType) -> None:
        exception_msg = ''.join(_traceback.format_exception_only(type_, value))
        full_traceback_msg = ''.join(_traceback.format_exception(type_, value, traceback, chain=True))
        print(exception_msg +"\n" + full_traceback_msg, file=sys.stderr)


instance = None # type: Optional[Application]

def create_instance() -> None:
    global instance
    if instance is None:
        instance = Application(sys.argv)
    assert instance is not None

def get_instance() -> Application:
    global instance
    assert instance is not None
    return instance
