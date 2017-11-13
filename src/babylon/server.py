import asyncio
import datetime

from aiohttp import web

from .backend import FileSystemBackend

def create_web_app(backend, url_base):
  async def shorten_url(request):
    data = await request.json()

    url = data["url"]
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
  backend = FileSystemBackend(loop, "./data", 10)
  url_base = "http://localhost:8080"
  app = create_web_app(backend, url_base)
  web.run_app(app)
