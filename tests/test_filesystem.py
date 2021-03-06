import datetime 
import time
import pytest

from urlshortener.server import create_web_app
from urlshortener.backend import FileSystemBackend, RandomKeyGenerator

BASE = "https://www.my-service.com"
KEY_LENGTH = 10

@pytest.fixture
def cli(loop, test_client, tmpdir_factory):
  key_gen = RandomKeyGenerator(KEY_LENGTH)
  app = create_web_app(FileSystemBackend(loop, tmpdir_factory.mktemp("data"), key_gen), BASE)
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

async def test_stress(cli):
  for i in range(100):
    url = "https://www.foo.com/{}".format(i)
    resp = await cli.post("/shorten_url", json={"url": url})
    assert resp.status == 200

    data = await resp.json()
    key = data["shortened_url"][len(BASE) + 1:]

    resp = await cli.get("/{}".format(key), allow_redirects=False)
    assert resp.status == 302
    assert resp.headers["Location"] == url

async def test_not_found(cli):
  resp = await cli.post("/shorten_url", json={"url": "https://www.foo.com"})
  assert resp.status == 200

  resp = await cli.get("/notfound", allow_redirects=False)
  assert resp.status == 404

async def test_invalid_url_400(cli):
  resp = await cli.post("/shorten_url", json={"url": "https://invalid.x"})
  assert resp.status == 400

 
