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

    def __init__(self,
                 api_key: str,
                 data_dir: pathlib.Path = pathlib.Path.cwd()) -> None:
        self._api_key: str = api_key
        self.data_dir: pathlib.Path = data_dir

    async def submit_scan_request(self, url: str) -> uuid.UUID:
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "API-Key": self._api_key
        }
        payload: Dict[str, str] = {
            "url": url,
            "public": "on"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{self.URLSCAN_API_URL}/scan/",
                    headers=headers,
                    data=json.dumps(payload)
            ) as response:
                r = await response.json()
                return uuid.UUID(r["uuid"])

    async def fetch_result(self, scan_uuid: uuid.UUID) -> Dict[str, Union[str, pathlib.Path]]:
        result_url: str = \
            "{api_url}/result/{uuid}".format(api_url=self.URLSCAN_API_URL, uuid=scan_uuid)

        async with aiohttp.ClientSession() as session:
            async with session.get(result_url) as response:
                r = await response.json()
                return {
                    "report": r["task"]["reportURL"],
                    "screenshot": await self.download_screenshot(r["task"]["screenshotURL"]),
                    "dom": await self.download_dom(scan_uuid, r["task"]["domURL"])
                }

    async def download_screenshot(self, screenshot_url: str) -> pathlib.Path:
        screenshot_name: str = screenshot_url.split("/")[-1]
        screenshot_location: str = f"{self.data_dir}/screenshots/{screenshot_name}"
        async with aiohttp.ClientSession() as session:
            async with session.get(screenshot_url) as response:
                if response.status == 200:
                    image_data = await aiofiles.open(screenshot_location, mode="wb")
                    await image_data.write(await response.read())
                    await image_data.close()
                    return screenshot_location

    async def download_dom(self, scan_uuid: uuid.UUID, dom_url: str) -> pathlib.Path:
        async with aiohttp.ClientSession() as session:
            async with session.get(dom_url) as response:
                if response.status == 200:
                    dom = await response.text()
                    dom_location: pathlib.Path = pathlib.Path(
                        "{data_dir}/doms/{uuid}.txt".format(data_dir=self.data_dir, uuid=scan_uuid)
                    )
                    with open(dom_location, "w", encoding="utf-8") as dom_file:
                        print(dom, file=dom_file)
                    return dom_location


        dom.encoding = "utf-8"
        dom_location: pathlib.Path = pathlib.Path(
            "{data_dir}/doms/{uuid}.txt".format(data_dir=self.data_dir, uuid=scan_uuid)
        )
        with open(dom_location, "w", encoding="utf-8") as dom_file:
            print(dom.text, file=dom_file)

        return dom_location

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

    url_scan = UrlScanAsync(
        api_key=api_key,
        data_dir=data_dir
    )

    print(f"started at {time.strftime('%X')}")
    print(await json.dumps(url_scan.investigate("https://www.google.com")))
    print(f"finished at {time.strftime('%X')}")


asyncio.run(main())
