from abc import ABCMeta, abstractmethod
import asyncio


class AsyncApp(metaclass=ABCMeta):
    @abstractmethod
    async def main(self) -> None: ...

    def start(self) -> None:
        event_loop = asyncio.get_event_loop()
        try:
            event_loop.run_until_complete(self.main())
        finally:
            event_loop.close()
