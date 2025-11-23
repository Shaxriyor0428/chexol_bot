import httpx


class APIClient:
    BASE_URL = "http://127.0.0.1:8000"

    def __init__(self, token: str = None, timeout: int = 10):
        self.token = token
        self.timeout = timeout

        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=self.timeout,
            headers=self._build_headers()
        )

    def _build_headers(self):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def get(self, url: str, params: dict = None):
        return await self._request("GET", url, params=params)

    async def post(self, url: str, data: dict = None):
        return await self._request("POST", url, json=data)

    async def put(self, url: str, data: dict = None):
        return await self._request("PUT", url, json=data)

    async def delete(self, url: str):
        return await self._request("DELETE", url)

    async def _request(self, method: str, url: str, **kwargs):
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "error": True,
                "status": e.response.status_code,
                "detail": e.response.text
            }
        except httpx.RequestError as e:
            return {"error": True, "detail": str(e)}

    async def set_token(self, token: str):
        """Tokenni yangilash"""
        self.token = token
        self.client.headers["Authorization"] = f"Bearer {token}"

    async def close(self):
        await self.client.aclose()
