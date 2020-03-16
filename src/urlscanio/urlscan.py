import asyncio
import json
import logging
import sys
from pathlib import Path
from uuid import UUID

import aiofiles
import aiohttp

logging.basicConfig()

class UrlScan:
    URLSCAN_API_URL = "https://urlscan.io/api/v1"
    DEFAULT_PAUSE_TIME = 3
    DEFAULT_MAX_ATTEMPTS = 10

    def __init__(self, api_key, data_dir=Path.cwd(), log_level=0):
        self.api_key = api_key
        self.data_dir = data_dir
        self.session = aiohttp.ClientSession(trust_env=True)
        self.verbose = True
        self.logger = logging.getLogger("urlscanio")
        self.logger.setLevel(log_level)

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
            self.logger.debug("%s request made to %s with %d response code", method, url, response.status)
            return response.status, await response.read()

    async def save_file(self, target_path, content):
        self.logger.debug("Creating and saving %s", target_path)
        async with aiofiles.open(target_path, "wb") as data:
            await data.write(content)

    async def submit_scan_request(self, url, private=False):
        self.logger.info("Requesting scan for %s", url)
        headers = {"Content-Type": "application/json", "API-Key": self.api_key}
        payload = {"url": url} if private else {"url": url, "public": "on"} 
        _, response = await self.execute("POST", f"{self.URLSCAN_API_URL}/scan/", headers, payload)
        body = json.loads(response)
        return UUID(body["uuid"])

    async def fetch_result(self, scan_uuid):
        self.logger.info("Requesting scan results for %s", scan_uuid)
        _, response = await self.execute("GET", f"{self.URLSCAN_API_URL}/result/{scan_uuid}")
        body = json.loads(response)
        return {
            "report": body["task"]["reportURL"],
            "screenshot": await self.download_screenshot(body["task"]["screenshotURL"]),
            "dom": await self.download_dom(scan_uuid, body["task"]["domURL"])
        }

    async def download_screenshot(self, screenshot_url):
        self.logger.info("Downloading screenshot from %s", screenshot_url)
        screenshot_name = screenshot_url.split("/")[-1]
        screenshot_location = Path(f"{self.data_dir}/screenshots/{screenshot_name}")
        status, response = await self.execute("GET", screenshot_url)
        if status == 200:
            await self.save_file(screenshot_location, response)
            return str(screenshot_location)

    async def download_dom(self, scan_uuid, dom_url):
        self.logger.info("Downloading DOM from %s", dom_url)
        dom_location = Path(f"{self.data_dir}/doms/{scan_uuid}.txt")
        status, response = await self.execute("GET", dom_url)
        if status == 200:
            await self.save_file(dom_location, response)
            return str(dom_location)

    async def investigate(self, url, private=False):
        self.logger.info("Starting investigation of %s", url)
        self.logger.debug("Default sleep time between attempts: %d, maximum number of attempts: %d",
                          self.DEFAULT_PAUSE_TIME, self.DEFAULT_MAX_ATTEMPTS)
        scan_uuid = await self.submit_scan_request(url, private)

        attempts = 0
        await asyncio.sleep(self.DEFAULT_PAUSE_TIME)
        while attempts < self.DEFAULT_MAX_ATTEMPTS:
            self.logger.debug("Loading scan output: attempt #%d", attempts)
            try:
                return await self.fetch_result(scan_uuid)
            except KeyError:
                attempts += 1
                await asyncio.sleep(self.DEFAULT_PAUSE_TIME)
        print(f"\nCould not fetch scan output after {attempts} attempts. Please try again.\n", file=sys.stderr)
        sys.exit(1)
