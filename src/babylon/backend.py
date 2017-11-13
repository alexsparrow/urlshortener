import random
import string
import os.path
import asyncio.locks

class Backend:
  async def shorten(self, url):
    """Shorten a given URL and return the key"""
    pass

  async def lengthen(self, key):
    """Given a shortened URL key, return the full URL"""
    pass

class FileSystemBackend(Backend):
  def __init__(self, loop, path, url_length):
    self._loop = loop
    self._path = path
    self._url_length = url_length
    self._lock = asyncio.locks.Lock(loop=loop)

  async def _run_blocking(self, func):
    return await self._loop.run_in_executor(None, func)

  def _write_key_if_unique(self, path, url):
    if not os.path.exists(path):
      with open(path, "w") as f:
        f.write(url)
      return True
    return False

  def _read_key(self, path):
    if not os.path.exists(path):
      return None
    else:
      with open(path) as f:
        return f.read()

  async def shorten(self, url):
    while True:
      key = "".join(random.choice(string.ascii_letters) for i in range(self._url_length))
      path = os.path.join(self._path, key)
      with await self._lock:
        if await self._run_blocking(lambda: self._write_key_if_unique(path, url)):
          return key

  async def lengthen(self, key):
    path = os.path.join(self._path, key)

    return await self._run_blocking(lambda: self._read_key(path))

  