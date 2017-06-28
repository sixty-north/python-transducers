import asyncio

from transducer.functional import compose
from transducer.transducers import enumerating, windowing


async def ticker(delay, to):
    """Yield numbers from 0 to `to` every `delay` seconds."""
    for i in range(to):
        yield i
        await asyncio.sleep(delay)


async def counter(delay, to):
    # from transducer.coop import transduce
    # from transducer.reducers import effecting
    # await transduce(
    #     transducer=compose(
    #         enumerating(),
    #         windowing(3)
    #     ),
    #     reducer=effecting(print),
    #     aiterable=ticker(delay, to)
    # )

    from transducer.lazy_coop import transduce
    async for item in transduce(
            transducer=compose(
                enumerating(),
                windowing(3)
            ),
            aiterable=ticker(delay, to)
    ):
        print(item)


def main():
    loop = asyncio.get_event_loop()

    task = asyncio.ensure_future(counter(2.0, 20))
    loop.run_until_complete(task)


if __name__ == '__main__':
    main()
