import asyncio
import aiohttp
import traceback
from functools import wraps


connection_exceptions = (aiohttp.ClientError, aiohttp.ClientConnectionError)

def retry_on_failure(retries=3, delay=2, exceptions=()):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < retries:
                try:
                    return await func(*args, **kwargs)
                except connection_exceptions as e:
                    attempts += 1
                    if attempts < retries:
                        print(f"Connection error: {e}. Retrying {attempts}/{retries} in {delay} seconds...")
                        await asyncio.sleep(delay)
                    else:
                        print(f"Failed after {retries} attempts.")
                        raise
                except Exception as e:
                    traceback.print_exc()
                    raise
        return wrapper
    return decorator
