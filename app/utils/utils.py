import asyncio
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
genesis_path = os.path.join(script_dir, "bootstrap_data", "genesis.txt")

def set_timeout(callback, delay: float):
    async def wrapper():
        await asyncio.sleep(delay)
        await callback() if asyncio.iscoroutinefunction(callback) else callback()
    asyncio.create_task(wrapper())

def get_genesis_txns():
    with open(genesis_path, "r") as f:
        content = f.read()
    return content