from enum import Enum
import attr
from typing import List
from cryfs.e2etest.utils.logger import Logger, LogLevel


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
    test_case_name: str
    log: Logger

    def status(self) -> TestStatus:
        if self.log.contains_entry_with_level(LogLevel.FATAL):
            return TestStatus.FATAL
        elif self.log.contains_entry_with_level(LogLevel.ERROR):
            return TestStatus.ERROR
        else:
            return TestStatus.SUCCESS

    def print(self) -> None:
        print("-------------------------")
        print("Detailed result for:")
        print("[%s] %s" % (self.status().to_string(), self.test_case_name))
        print("-------------------------")
        print(self.log.to_string())
        print()


class TestResults(object):
    def __init__(self, results: List[TestResult]) -> None:
        self._results = results

    def status(self) -> TestStatus:
        fatalled = [r for r in self._results if r.status() == TestStatus.FATAL]
        if len(fatalled) != 0:
            return TestStatus.FATAL
        errored = [r for r in self._results if r.status() == TestStatus.ERROR]
        if len(errored) != 0:
            return TestStatus.ERROR
        return TestStatus.SUCCESS

    def print(self) -> None:
        print("-------------------------")
        print("Summary")
        print("-------------------------")
        for result in self._results:
            print("[%s] %s" % (result.status().to_string(), result.test_case_name))
        print()
        for fatalled in [r for r in self._results if r.status() == TestStatus.FATAL]:
            fatalled.print()
        for errored in [r for r in self._results if r.status() == TestStatus.ERROR]:
            errored.print()
