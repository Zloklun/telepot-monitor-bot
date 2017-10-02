
import asyncio as aio

def sync_exec(coro):
    aio.ensure_future(coro)
