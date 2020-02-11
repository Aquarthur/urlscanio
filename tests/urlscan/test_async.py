import json
from typing import Any, Dict
from uuid import UUID

import pytest
from aioresponses import aioresponses
from pytest_mock import MockFixture

from ..context import urlscan_async


# Utility function to allow for mocking async function returns
async def return_async(val: Any) -> Any:
    return val


@pytest.mark.asyncio
async def test_submit_scan_request(test_urlscan_params: Dict[str, Any],
                                   submit_response: Dict[str, Any]) -> None:
    with aioresponses() as mocked:
        mocked.post(test_urlscan_params["submit_url"], status=200, body=json.dumps(submit_response))
        async with urlscan_async.UrlScanAsync(
            api_key=test_urlscan_params["api_key"],
            data_dir=test_urlscan_params["data_dir"]) as urlscan:
            actual: UUID = await urlscan.submit_scan_request("https://www.test.com")
            assert UUID(submit_response["uuid"]) == actual


@pytest.mark.asyncio
async def test_fetch_result(mocker,
                            test_urlscan_params: Dict[str, Any],
                            success_result_response: Dict[str, Any]) -> None:
    # Mock download_screenshot function
    mock_download_screenshot: MockFixture = mocker.patch("src.urlscanio.urlscan_async.UrlScanAsync.download_screenshot")
    mock_download_screenshot.return_value = return_async(test_urlscan_params["screenshot"]["path"])
    # Mock download_dom function
    mock_download_dom: MockFixture = mocker.patch("src.urlscanio.urlscan_async.UrlScanAsync.download_dom")
    mock_download_dom.return_value = return_async(test_urlscan_params["dom"]["path"])

    with aioresponses() as mocked:
        mocked.get(test_urlscan_params["result_url"],
                   status=200,
                   body=json.dumps(success_result_response))

        async with urlscan_async.UrlScanAsync(
            api_key=test_urlscan_params["api_key"],
            data_dir=test_urlscan_params["data_dir"]) as urlscan:
            actual: Dict[str, str] = await urlscan.fetch_result(test_urlscan_params["uuid"])
            mock_download_screenshot.assert_called_once_with(test_urlscan_params["screenshot"]["link"])
            mock_download_dom.assert_called_once_with(
                test_urlscan_params["uuid"],
                test_urlscan_params["dom"]["link"]
            )

            assert f"https://urlscan.io/result/{test_urlscan_params['uuid']}/" == actual["report"]
            assert test_urlscan_params["screenshot"]["path"] == actual["screenshot"]
            assert test_urlscan_params["dom"]["path"] == actual["dom"]


@pytest.mark.asyncio
async def test_download_screenshot(mocker,
                                   test_urlscan_params: Dict[str, Any],
                                   screenshot_response: Any) -> None:
    mock_save_file = mocker.patch("src.urlscanio.urlscan_async.UrlScanAsync.save_file")
    mock_save_file.return_value = return_async(None)

    with aioresponses() as mocked:
        mocked.get(test_urlscan_params["screenshot"]["link"],
                   status=200,
                   body=screenshot_response)

        async with urlscan_async.UrlScanAsync(api_key=test_urlscan_params["api_key"],
                                              data_dir=test_urlscan_params["data_dir"]) as urlscan:
            actual: str = await urlscan.download_screenshot(test_urlscan_params["screenshot"]["link"])
            assert str(test_urlscan_params["screenshot"]["path"]) == actual
            mock_save_file.assert_called_once_with(test_urlscan_params["screenshot"]["path"], screenshot_response)


@pytest.mark.asyncio
async def test_download_dom(mocker,
                            test_urlscan_params: Dict[str, Any],
                            dom_response: Any) -> None:
    mock_save_file = mocker.patch("src.urlscanio.urlscan_async.UrlScanAsync.save_file")
    mock_save_file.return_value = return_async(None)

    with aioresponses() as mocked:
        mocked.get(test_urlscan_params["dom"]["link"],
                   status=200,
                   body=dom_response)

        async with urlscan_async.UrlScanAsync(api_key=test_urlscan_params["api_key"],
                                              data_dir=test_urlscan_params["data_dir"]) as urlscan:
            actual: str = await urlscan.download_dom(test_urlscan_params["uuid"], test_urlscan_params["dom"]["link"])
            assert str(test_urlscan_params["dom"]["path"]) == actual
            mock_save_file.assert_called_once()
