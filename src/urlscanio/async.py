import asyncio
import json
import os
import pathlib
import time
import uuid
from typing import Any, Dict, Optional, Union

import aiofiles
import aiohttp
import utils


class UrlScanAsync:

    URLSCAN_API_URL: str = "https://urlscan.io/api/v1"
    DEFAULT_PAUSE_TIME: int = 3
    DEFAULT_MAX_CALLS: int = 10

    def __init__(self, api_key: str, data_dir: pathlib.Path = pathlib.Path.cwd()):
        self.api_key = api_key
        self.data_dir = data_dir
        self.session = aiohttp.ClientSession(trust_env=True)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *excinfo):
        await self.session.close()

    async def get(self, url: str) -> Any:
        async with self.session.get(url, ssl=False) as response:
            return response.status, await response.read()

    async def post(self, url: str, headers: Dict[str, str], payload: None) -> Any:
        async with self.session.post(
                url,
                headers=headers,
                data=json.dumps(payload),
                ssl=False) as response:
            return response.status, await response.read()

    async def submit_scan_request(self, url: str) -> uuid.UUID:
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "API-Key": self.api_key
        }
        payload: Dict[str, str] = {
            "url": url,
            "public": "on"
        }

        _, response = await self.post(f"{self.URLSCAN_API_URL}/scan/", headers, payload)
        body = json.loads(response)
        return uuid.UUID(body["uuid"])

    async def fetch_result(self, scan_uuid: uuid.UUID) -> Dict[str, Union[str, pathlib.Path]]:
        result_url: str = \
            "{api_url}/result/{uuid}".format(api_url=self.URLSCAN_API_URL, uuid=scan_uuid)
        _, response = await self.get(result_url)
        body: Dict[str, Any] = json.loads(response)
        return {
            "report": body["task"]["reportURL"],
            "screenshot": await self.download_screenshot(body["task"]["screenshotURL"]),
            "dom": await self.download_dom(scan_uuid, body["task"]["domURL"])
        }

    async def download_screenshot(self, screenshot_url: str) -> str:
        screenshot_name: str = screenshot_url.split("/")[-1]
        screenshot_location: pathlib.Path = pathlib.Path(f"{self.data_dir}/screenshots/{screenshot_name}")

        status, response = await self.get(screenshot_url)
        if status == 200:
            image_data = await aiofiles.open(screenshot_location, mode="wb")
            await image_data.write(response)
            await image_data.close()
            return str(screenshot_location)

    async def download_dom(self, scan_uuid: uuid.UUID, dom_url: str) -> str:
        dom_location: pathlib.Path = pathlib.Path(f"{self.data_dir}/doms/{scan_uuid}.txt")
        status, response = await self.get(dom_url)
        if status == 200:
            dom_data = await aiofiles.open(dom_location, mode="wb")
            await dom_data.write(response)
            await dom_data.close()
            return str(dom_location)

    async def investigate(self, url: str) -> Dict[str, Union[str, pathlib.Path]]:
        scan_uuid: uuid.UUID = await self.submit_scan_request(url)        
        result: Optional[Dict[str, Union[str, pathlib.Path]]] = None

        calls = 0
        await asyncio.sleep(self.DEFAULT_PAUSE_TIME)
        while not result:
            try:
                result = await self.fetch_result(scan_uuid)
            except KeyError:
                calls += 1
                await asyncio.sleep(self.DEFAULT_PAUSE_TIME)

        return result if result is not None else \
               {"error": "Your request timed out. Please try again."}

async def main():
    api_key: str = os.environ["URLSCAN_API_KEY"]
    data_dir: pathlib.Path = pathlib.Path(os.getenv("URLSCAN_DATA_DIR", "."))
    utils.create_data_dir(data_dir)

    async with UrlScanAsync(api_key=api_key, data_dir=data_dir) as url_scan:
        print(f"started at {time.strftime('%X')}")
        print(json.dumps(await url_scan.investigate("https://www.google.com")))
        print(f"finished at {time.strftime('%X')}")


asyncio.run(main())
