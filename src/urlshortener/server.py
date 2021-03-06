import asyncio
import datetime
import os

from aiohttp import web
import validators

from .backend import FileSystemBackend, RandomKeyGenerator

def validate_url(url):
  return bool(validators.url(url))

def create_web_app(backend, url_base):
  async def shorten_url(request):
    data = await request.json()

    url = data["url"]
    if not validate_url(url):
      return web.HTTPBadRequest()

    short_url = "{}/{}".format(url_base, await backend.shorten(url))

    return web.json_response({
      "shortened_url": short_url
    })

  async def lengthen_url(request):
    key = request.match_info["key"]
    url = await backend.lengthen(key)

    if url:
      return web.HTTPFound(url)
    else:
      return web.HTTPNotFound()


  app = web.Application()
  app.router.add_post('/shorten_url', shorten_url)
  app.router.add_get('/{key}', lengthen_url)
  return app

if __name__ == "__main__":
  loop = asyncio.get_event_loop()

  # The root of shortened URLs (without trailing slash)
  url_base = os.environ.get("URLSHORTENER_URL_BASE", "http://localhost:8080")

  # The root directory for storing application state
  data_dir = os.environ.get("URLSHORTENER_DATA_DIR", "./data")

  # A prefix to use for generated URLs if multiple replicas are sharing a filesystem
  key_prefix = os.environ.get("URLSHORTENER_KEY_PREFIX", "")

  key_gen = RandomKeyGenerator(10, prefix=key_prefix)
  backend = FileSystemBackend(loop, data_dir, key_gen)

  app = create_web_app(backend, url_base)
  web.run_app(app)
