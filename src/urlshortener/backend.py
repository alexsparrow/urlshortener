import random
import string
import os.path
import asyncio.locks

class KeyGenerator:
  def generate(self):
    pass

class RandomKeyGenerator(KeyGenerator):
  def __init__(self, key_length, prefix=""):
    self._key_length = key_length
    self._prefix = prefix

  def generate(self):
    rand_key = "".join(random.choice(string.ascii_letters) for i in range(self._key_length))
    return self._prefix + rand_key

class KVBackend:
  async def shorten(self, url):
    """Shorten a given URL and return the key"""
    pass

  async def lengthen(self, key):
    """Given a shortened URL key, return the full URL"""
    pass

class FileSystemBackend(KVBackend):
  """
  A basic backend to store shortened URLs flat in the filesystem

  NOTE that since the file APIs are blocking, this class isn't currently able to take advantage of asynchronous I/O.
  """
  def __init__(self, loop, path, key_gen):
    self._loop = loop
    self._path = path
    self._key_gen = key_gen
    self._lock = asyncio.locks.Lock(loop=loop)

  async def _run_blocking(self, func):
    return await self._loop.run_in_executor(None, func)

  def _write_key_if_unique(self, path, url):
    # I think this logic can be better done with an atomic rename (on Linux at least)
    # That avoids the race condition between exists and write and obviates the need
    # for a lock.
    if not os.path.exists(path):
      self._make_dirs(path)

      with open(path, "w") as f:
        f.write(url)
      return True

    return False

  def _read_key(self, path):
    if not os.path.exists(path):
      return None
    with open(path) as f:
      return f.read()

  def _make_path(self, key):
    # NOTE: to support a larger keyspace, this might split the key up into subdirectories
    return os.path.join(self._path, key)

  def _make_dirs(self, path):
    # Create the directory if necessary
    dir_name = os.path.dirname(path)
    if not os.path.exists(dir_name):
      os.makedirs(dir_name)

  async def shorten(self, url):
    while True:
      key = self._key_gen.generate()
      path = self._make_path(key)
      with await self._lock:
        if await self._run_blocking(lambda: self._write_key_if_unique(path, url)):
          return key

  async def lengthen(self, key):
    path = self._make_path(key)
    return await self._run_blocking(lambda: self._read_key(path))

class InMemoryBackend(KVBackend):
  def __init__(self, loop, key_gen):
    self._key_gen = key_gen
    self._store = {}
    self._lock = asyncio.locks.Lock(loop=loop)

  async def shorten(self, url):
    while True:
      key = self._key_gen.generate()
      with await self._lock:
        if not key in self._store:
          self._store[key] = url
          return key

  async def lengthen(self, key):
    return self._store.get(key, None)

