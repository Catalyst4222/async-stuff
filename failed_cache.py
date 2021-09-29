import asyncio


class Cache:
    def __init__(self, method):
        self._method = method

    def __await__(self):
        meth = self._method().__await__()
        if hasattr(meth, '__await__'):
            meth = meth.__await__()
        return meth


# def async_cache(method):
#     return method.__await__()


# noinspection PyMethodMayBeStatic
class C:
    def __init__(self):
        print('Made it to C!')

    async def c_func(self):
        print('Made it to the end')


# noinspection PyMethodMayBeStatic
class B:
    def __init__(self):
        print('Made it to B!')

    async def b_func(self) -> C:
        return C()


# noinspection PyMethodMayBeStatic
class A:
    def __init__(self):
        print('Made it to A!')

    async def a_func(self):
        return Cache(B)


async def main():

    await A().a_func().b_func().c_func()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())