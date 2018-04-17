from abc import ABCMeta, abstractmethod
from typing import Iterable
from cryfs.e2etest.test_framework.logger import Logger


class ITestCase(object, metaclass=ABCMeta):
    @abstractmethod
    async def run(self, logger: Logger) -> None: ...

    @abstractmethod
    def name(self) -> str: ...


class ITestSuite(object, metaclass=ABCMeta):
    @abstractmethod
    def test_cases(self) -> Iterable[ITestCase]: ...
