import typing
import asyncio
import functools

# taken from `?tag to_thread deco` in the dpy server
def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # The to_thread coroutine runs the sync function in another thread
        # and then returns the result. This achieves the same result as
        # run_in_executor for people who are on <3.9 but using this makes
        # for even more clean code.
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper
