import asyncio
import json
from pathlib import Path
from uuid import UUID

import aiofiles
import aiohttp


class UrlScan:
    URLSCAN_API_URL = "https://urlscan.io/api/v1"
    DEFAULT_PAUSE_TIME = 3
    DEFAULT_MAX_CALLS = 10

    def __init__(self, api_key, data_dir=Path.cwd()):
        self.api_key = api_key
        self.data_dir = data_dir
        self.session = aiohttp.ClientSession(trust_env=True)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *excinfo):
        await self.session.close()

    async def execute(self, method, url, headers=None, payload=None):
        async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                data=json.dumps(payload),
                ssl=False) as response:
            return response.status, await response.read()

    async def save_file(self, target_path, content):
        async with aiofiles.open(target_path, "wb") as data:
            await data.write(content)

    async def submit_scan_request(self, url):
        headers = {"Content-Type": "application/json", "API-Key": self.api_key}
        payload = {"url": url, "public": "on"}
        _, response = await self.execute("POST", f"{self.URLSCAN_API_URL}/scan/", headers, payload)
        body = json.loads(response)
        return UUID(body["uuid"])

    async def fetch_result(self, scan_uuid):
        _, response = await self.execute("GET", f"{self.URLSCAN_API_URL}/result/{scan_uuid}")
        body = json.loads(response)
        return {
            "report": body["task"]["reportURL"],
            "screenshot": await self.download_screenshot(body["task"]["screenshotURL"]),
            "dom": await self.download_dom(scan_uuid, body["task"]["domURL"])
        }

    async def download_screenshot(self, screenshot_url):
        screenshot_name = screenshot_url.split("/")[-1]
        screenshot_location = Path(f"{self.data_dir}/screenshots/{screenshot_name}")
        status, response = await self.execute("GET", screenshot_url)
        if status == 200:
            await self.save_file(screenshot_location, response)
            return str(screenshot_location)

    async def download_dom(self, scan_uuid, dom_url):
        dom_location = Path(f"{self.data_dir}/doms/{scan_uuid}.txt")
        status, response = await self.execute("GET", dom_url)
        if status == 200:
            await self.save_file(dom_location, response)
            return str(dom_location)

    async def investigate(self, url):
        scan_uuid = await self.submit_scan_request(url)
        result = None

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
