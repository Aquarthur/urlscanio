import asyncio
import json
from pathlib import Path
from typing import Any, Dict, Union
from uuid import UUID

import aiofiles
import aiohttp


class UrlScanAsync:

    URLSCAN_API_URL: str = "https://urlscan.io/api/v1"
    DEFAULT_PAUSE_TIME: int = 3
    DEFAULT_MAX_CALLS: int = 10

    def __init__(self, api_key: str, data_dir: str = Path.cwd()) -> None:
        self.api_key = api_key
        self.data_dir = data_dir
        self.session = aiohttp.ClientSession(trust_env=True)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *excinfo) -> None:
        await self.session.close()

    async def execute(self,
                      method: str,
                      url: str,
                      headers: Dict[str, str] = None,
                      payload: Dict[str, str] = None) -> (int, bytes):
        async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                data=json.dumps(payload),
                ssl=False) as response:
            return response.status, await response.read()

    async def save_file(self, target_path: str, content: Any) -> None:
        async with aiofiles.open(target_path, "wb") as data:
            await data.write(content)

    async def submit_scan_request(self, url: str) -> UUID:
        headers: Dict[str, str] = {"Content-Type": "application/json", "API-Key": self.api_key}
        payload: Dict[str, str] = {"url": url, "public": "on"}
        _, response = await self.execute("POST", f"{self.URLSCAN_API_URL}/scan/", headers, payload)
        body = json.loads(response)
        return UUID(body["uuid"])

    async def fetch_result(self, scan_uuid: UUID) -> Dict[str, Union[str, Path]]:
        _, response = await self.execute("GET", f"{self.URLSCAN_API_URL}/result/{scan_uuid}")
        body: Dict[str, Any] = json.loads(response)
        return {
            "report": body["task"]["reportURL"],
            "screenshot": await self.download_screenshot(body["task"]["screenshotURL"]),
            "dom": await self.download_dom(scan_uuid, body["task"]["domURL"])
        }

    async def download_screenshot(self, screenshot_url: str) -> str:
        screenshot_name: str = screenshot_url.split("/")[-1]
        screenshot_location: Path = Path(f"{self.data_dir}/screenshots/{screenshot_name}")
        status, response = await self.execute("GET", screenshot_url)
        if status == 200:
            await self.save_file(screenshot_location, response)
            return str(screenshot_location)

    async def download_dom(self, scan_uuid: UUID, dom_url: str) -> str:
        dom_location: Path = Path(f"{self.data_dir}/doms/{scan_uuid}.txt")
        status, response = await self.execute("GET", dom_url)
        if status == 200:
            await self.save_file(dom_location, response)
            return str(dom_location)

    async def investigate(self, url: str) -> Dict[str, str]:
        scan_uuid: UUID = await self.submit_scan_request(url)
        result: Dict[str, Union[str, Path]] = None

        calls = 0
        await asyncio.sleep(self.DEFAULT_PAUSE_TIME)
        while not result and calls < self.DEFAULT_MAX_CALLS:
            try:
                result = await self.fetch_result(scan_uuid)
            except KeyError:
                calls += 1
                await asyncio.sleep(self.DEFAULT_PAUSE_TIME)

        return result if result is not None else \
               {"error": "Your request timed out. Please try again."}
