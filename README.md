# URL Shortener
This is a basic URL shortener service written using Python `asyncio` and `aiohttp`. The default
filesystem backend stores data flat in a folder but adding additional backends is straightforward. 

The default filesystem backend using blocking IO which kind of defeats the purpose of using `asyncio`.

## Running
To setup the Python requirements for this service:

```
pip install -r requirements.txt
```

To run this service:

```
export URLSHORTENER_URL_BASE=https://www.base-url.com
export URLSHORTENER_DATA_DIR=/path/to/data

PYTHONPATH=src python -m  urlshortener.server
```

To run the tests:

```
PYTHONPATH=src pytest
```

## Scaling
To achieve straightforward scaling, set the base URL on each node (`<number>=0..n`) to e.g. `https://www.base-url.com/<number>` and setup a suitable reverse proxy (e.g. nginx) to forward traffic to each node on the appropriate path.

Alternatively point the data directory at a shared filesystem and configure the reverse proxy to load balance across the nodes. You will need to configure `URLSHORTENER_KEY_PREFIX` with a unique string to ensure that each replica generates unique URL keys.