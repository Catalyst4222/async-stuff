import asyncio, random

from buses import EventBus

async def pull_trigger(bus: EventBus):
    await asyncio.sleep(1)
    bus.emit('bang', leave_open=True)


async def player(name, bus: EventBus):
    await asyncio.sleep(random.random())
    print(f'Runner {name} is ready!')
    await bus.wait_for_event('bang')
    await asyncio.sleep(5 * random.random())
    print(f'Runner {name} has finished!')


async def late_player(name, bus: EventBus):
    await asyncio.sleep(random.random() + 1)
    print(f'Oh no! {name} is late!')
    await bus.wait_for_event('bang')
    await asyncio.sleep(5 * random.random())
    print(f'Late runner {name} has finished!')


async def main():
    loop = asyncio.get_running_loop()
    bus = EventBus()
    bus.create_event('bang')
    loop.create_task(pull_trigger(bus=bus))

    [
        loop.create_task(player(name, bus))
        for name in
        ['Alice', 'Bob', 'Charlie', 'Danny']
    ]

    loop.create_task(late_player('John', bus))

    print('Take your marks...')
    await bus.wait_for_event('bang')
    print('Shot fired!')

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop