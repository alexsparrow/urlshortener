import datetime 
import time
import pytest

from urlshortener.server import create_web_app
from urlshortener.backend import InMemoryBackend, RandomKeyGenerator

BASE = "https://www.my-service.com"
KEY_LENGTH = 10

@pytest.fixture
def cli(loop, test_client, tmpdir_factory):
  key_gen = RandomKeyGenerator(KEY_LENGTH)
  app = create_web_app(InMemoryBackend(loop, key_gen), BASE)
  return loop.run_until_complete(test_client(app))

async def test_basic(cli):
  resp = await cli.post("/shorten_url", json={"url": "https://www.foo.com"})
  assert resp.status == 200

  data = await resp.json()

  assert data["shortened_url"].startswith(BASE)

  key = data["shortened_url"][len(BASE) + 1:]
  assert len(key) == KEY_LENGTH

  resp = await cli.get("/{}".format(key), allow_redirects=False)

  assert resp.status == 302
  assert resp.headers["Location"] == "https://www.foo.com"

