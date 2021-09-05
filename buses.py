from asyncio import Future, wait, get_running_loop, AbstractEventLoop, Event
from typing import Any, Optional, Dict

class PartnerBus:  # Version of EventBus that swaps 2 results
    """.warn : Currently completely untested"""
    def __init__(self, *, loop: Optional[AbstractEventLoop] = None):
        self.futures: Dict[StopIteration, tuple[Future, Any]] = {}
        self._loop = loop or get_running_loop()

    def get_future(self, event: str, value: Any) -> Future:
        if self.futures.get(event):
            future: Future = self.futures[event][0]
            future.set_result(value)  # Set partner's future to given value

            new_fut = Future()
            new_fut.set_result(self.futures[event][1])
            return future  # Set own future to partner's value

        else:
            self.futures[event] = (Future(), value)
            return self.futures[event][0]

    async def wait_for_two(self, event: str, value: Any, timeout: Optional[float] = None) -> Any:
        """Takes an event, value, and timeout
        If it's the first of two calls, it will yield until the second call is made
        The value passed will be the return value of the other call, and vice versa
        If it times out, the event will be cleared and `TimeoutError` will be raised
        """
        future = self.get_future(event, value)

        done, pending = await wait([future], timeout=timeout)

        if not len(done):
            del self.futures[event]
            raise TimeoutError

        return future.result()



class EventBus:  # Fix soonish
    def __init__(self, *, loop: Optional[AbstractEventLoop] = None):
        self.events: Dict[str, dict] = {}
        self._loop = loop or get_running_loop()

    def create_event(self, event: str) -> None:
        self.events[event] = {'futures': [], 'open': False}

    def wait_for_event(self, event: str) -> Future:
        fut = self._loop.create_future()
        self.events[event]['futures'].append(fut)

        if self.events[event]['open']:
            fut.set_result(None)

        return fut

    def close_event(self, event: str) -> None:
        self.events[event]['open'] = False

    def emit(self, event: str, *, leave_open: bool = False) -> None:
        for fut in self.events[event]['futures']:
            fut.set_result(None)

        self.events[event]['open'] = leave_open


# TODO bus for one shot thing

class EventManager:
    def __init__(self, *, loop: Optional[AbstractEventLoop] = None):
        self._loop = loop or get_running_loop()
        self.events: dict[str, Event] = {}

    async def wait_for_event(self, event: str) -> None:
        await self.events[event].wait()

    def set_event(self, event: str) -> None:
        self.events[event].set()

    def new_event(self, event: str) -> None:
        self.events[event] = Event(loop=self._loop)

