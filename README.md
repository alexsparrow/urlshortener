# URL Shortener

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

Alternatively point the data directory at a shared filesystem and configure the reverse proxy to load balance across the nodes.