# api-client

Implement or modify HTTP client with retry logic.

## Retry Policy

- 3 attempts, 2s initial backoff, doubles each retry
- 30s request timeout
- Retry on 500, 502, 503, 504 and `requests.RequestException`
- 4xx and 2xx returned immediately
- Raise `RuntimeError("Request failed after N attempts")` on exhaustion
