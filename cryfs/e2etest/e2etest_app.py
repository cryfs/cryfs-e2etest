import sys
import traceback as _traceback
from typing import List, Type, TypeVar, Optional
import asyncio
import argparse
from types import TracebackType
from cryfs.e2etest.fsmounter import CryfsMounter
from cryfs.e2etest.utils.async_app import AsyncApp
from cryfs.e2etest.test_framework.result import TestStatus, TestResult, TestResults
from cryfs.e2etest.test_framework.test_case import ITestCase, ITestSuite
from cryfs.e2etest.compatibility_test import CompatibilityTests
from cryfs.e2etest.readwrite_test import ReadWriteTests
from cryfs.e2etest.test_framework.logger import Logger, LogLevel


T = TypeVar('T')


class Application(AsyncApp):
    def __init__(self) -> None:
        self.args = self._parse_args()

    def _parse_args(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument('--cryfs-executable', default='/usr/bin/cryfs')
        return parser.parse_args()

    # TODO Auto-call this in run()
    def setupUncaughtExceptionHandler(self) -> None:
        sys.excepthook = self._onUncaughtException

    async def main(self) -> None:
        print(self.args.cryfs_executable)
        mounter = CryfsMounter(self.args.cryfs_executable)
        suites = [CompatibilityTests(mounter), ReadWriteTests(mounter)]
        test_cases = self._test_cases_from_suites(suites)
        results = await asyncio.gather(*[self._run_case(case) for case in test_cases])
        result = TestResults(results)
        result.print()
        if result.status() != TestStatus.SUCCESS:
            exit(1)

    def _test_cases_from_suites(self, suites: List[ITestSuite]) -> List[ITestCase]:
        return [case for suite in suites for case in suite.test_cases()]

    async def _run_case(self, case: ITestCase) -> TestResult:
        logger = Logger()
        try:
            await case.run(logger)
        except Exception as e:
            logger.log(LogLevel.FATAL, "Exception: " + _traceback.format_exc())
        return TestResult(test_case_name=case.name(), log=logger)


    def _onUncaughtException(self, type_: Type[BaseException], value: BaseException, traceback: TracebackType) -> None:
        exception_msg = ''.join(_traceback.format_exception_only(type_, value))
        full_traceback_msg = ''.join(_traceback.format_exception(type_, value, traceback, chain=True))
        print(exception_msg +"\n" + full_traceback_msg, file=sys.stderr)


instance = None # type: Optional[Application]

def create_instance() -> None:
    global instance
    if instance is None:
        instance = Application()
    assert instance is not None

def get_instance() -> Application:
    global instance
    assert instance is not None
    return instance
