# api-client

<!-- encoding: utf-8 -->

Implement or modify HTTP client with retry logic.

## Retry Policy

- 3 attempts, 2s initial backoff, doubles each retry
- 30s request timeout
- Retry on 500, 502, 503, 504 and `requests.RequestException`
- 4xx and 2xx returned immediately
- Raise `RuntimeError("Request failed after N attempts")` on exhaustion

## Code Pattern

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def make_session(retries=3, backoff=2, timeout=30):
    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=backoff,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def request_with_retry(method, url, **kwargs):
    session = make_session()
    try:
        resp = session.request(method, url, timeout=kwargs.pop("timeout", 30), **kwargs)
        resp.raise_for_status()
        return resp
    except requests.RequestException as e:
        raise RuntimeError(f"Request failed: {e}")
```

## Usage in this project

This project uses `requests` for API calls (Yandex Disk, VK OAuth, Google OAuth). When adding new HTTP clients, match the retry pattern above.
