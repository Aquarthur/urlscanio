import json
import pathlib
import time
import uuid
from io import BytesIO
from typing import Any, Dict, Optional, Union

from PIL import Image
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning  # pylint: disable=E0401

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)       # pylint: disable=E1101

class UrlScan:

    URLSCAN_API_URL: str = "https://urlscan.io/api/v1"
    DEFAULT_PAUSE_TIME: int = 3
    DEFAULT_MAX_CALLS: int = 10

    def __init__(self,
                 api_key: str,
                 proxies: Optional[Dict[str, str]] = None,
                 data_dir: pathlib.Path = pathlib.Path.cwd()) -> None:
        self._api_key: str = api_key
        self._proxies: Optional[Dict[str, str]] = proxies
        self.data_dir: pathlib.Path = data_dir

    def submit_scan_request(self, url: str) -> uuid.UUID:
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "API-Key": self._api_key
        }
        payload: Dict[str, str] = {
            "url": url,
            "public": "on"
        }
        response: Dict[str, Any] = requests.post(
            "{api_url}/scan/".format(api_url=self.URLSCAN_API_URL),
            headers=headers,
            data=json.dumps(payload),
            proxies=self._proxies,
            verify=False
        ).json()

        return uuid.UUID(response["uuid"])

    def fetch_result(self, scan_uuid: uuid.UUID) -> Dict[str, Union[str, pathlib.Path]]:
        result_url: str = \
            "{api_url}/result/{uuid}".format(api_url=self.URLSCAN_API_URL, uuid=scan_uuid)
        response: Dict[str, Any] = requests.get(
            result_url,
            proxies=self._proxies,
            verify=False
        ).json()

        return {
            "report": response["task"]["reportURL"],
            "screenshot": self.download_screenshot(response["task"]["screenshotURL"]),
            "dom": self.download_dom(scan_uuid, response["task"]["domURL"])
        }

    def download_screenshot(self, screenshot_url: str) -> pathlib.Path:
        screenshot_res: Any = \
            requests.get(screenshot_url, proxies=self._proxies, verify=False).content
        screenshot_name: str = screenshot_url.split("/")[-1]
        screenshot_location: pathlib.Path = pathlib.Path(
            "{data_dir}/screenshots/{name}".format(data_dir=self.data_dir, name=screenshot_name)
        )

        Image.open(BytesIO(screenshot_res)).save(screenshot_location)

        return screenshot_location

    def download_dom(self, scan_uuid: uuid.UUID, dom_url: str) -> pathlib.Path:
        dom: Any = requests.get(dom_url, proxies=self._proxies, verify=False)
        dom.encoding = "utf-8"
        dom_location: pathlib.Path = pathlib.Path(
            "{data_dir}/doms/{uuid}.txt".format(data_dir=self.data_dir, uuid=scan_uuid)
        )
        with open(dom_location, "w", encoding="utf-8") as dom_file:
            print(dom.text, file=dom_file)

        return dom_location

    def investigate(self, url: str) -> Dict[str, Union[str, pathlib.Path]]:
        scan_uuid: uuid.UUID = self.submit_scan_request(url)
        result: Optional[Dict[str, Union[str, pathlib.Path]]] = None
        calls: int = 0
        print("Fetching scan report. Please wait, this may take a while...")
        while not result and calls < self.DEFAULT_MAX_CALLS:
            try:
                result = self.fetch_result(scan_uuid)
            except KeyError:
                time.sleep(self.DEFAULT_PAUSE_TIME)
            calls += 1

        return result if result is not None else \
               {"error": "Your request timed out. Please try again."}
