from asyncio import Future, wait, get_running_loop, AbstractEventLoop
from typing import Any, Union, Optional, List, Dict

class PartnerBus:  # Version of EventBus that swaps 2 results
    """.warn : Currently completely untested"""
    def __init__(self):
        self.futures: Dict[int, tuple[Future, Any]] = {}

    def get_future(self, event: int, value: Any) -> Future:
        if self.futures.get(event):
            future: Future = self.futures[event][0]
            future.set_result(value)  # Set partner's future to given value

            new_fut = Future()
            new_fut.set_result(self.futures[event][1])
            return future  # Set own future to partner's value

        else:
            self.futures[event] = (Future(), value)
            return self.futures[event][0]

    async def wait_for_two(self, event: int, value: str, timeout: Optional[float] = None) -> Any:
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



class EventBus:  # The main thing I want to add to
    def __init__(self, *, loop: Optional[AbstractEventLoop] = None):
        self.events: Dict[str, dict] = {}

        if loop is None:
            self._loop: AbstractEventLoop = get_running_loop()
        else:
            self._loop: AbstractEventLoop = loop

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