import json

import pytest
from aioresponses import aioresponses

from ..context import urlscan


# Utility function to allow for mocking async function returns
async def return_async(val):
    return val


@pytest.mark.asyncio
async def test_submit_scan_request(test_urlscan_params, submit_response):
    with aioresponses() as mocked:
        mocked.post(test_urlscan_params["submit_url"], status=200, body=json.dumps(submit_response))
        async with urlscan.UrlScan(api_key=test_urlscan_params["api_key"],
                                   data_dir=test_urlscan_params["data_dir"]) as url_scan:
            actual = await url_scan.submit_scan_request("https://www.test.com")
            assert submit_response["uuid"] == actual


@pytest.mark.asyncio
async def test_fetch_result(mocker, test_urlscan_params, success_result_response):
    # Mock download_screenshot function
    mock_download_screenshot = mocker.patch("src.urlscanio.urlscan.UrlScan.download_screenshot")
    mock_download_screenshot.return_value = return_async(test_urlscan_params["screenshot"]["path"])
    # Mock download_dom function
    mock_download_dom = mocker.patch("src.urlscanio.urlscan.UrlScan.download_dom")
    mock_download_dom.return_value = return_async(test_urlscan_params["dom"]["path"])

    with aioresponses() as mocked:
        mocked.get(test_urlscan_params["result_url"],
                   status=200,
                   body=json.dumps(success_result_response))

        async with urlscan.UrlScan(api_key=test_urlscan_params["api_key"],
                                   data_dir=test_urlscan_params["data_dir"]) as url_scan:
            actual = await url_scan.fetch_result(test_urlscan_params["uuid"])
            mock_download_screenshot.assert_called_once_with(test_urlscan_params["screenshot"]["link"])
            mock_download_dom.assert_called_once_with(
                test_urlscan_params["uuid"],
                test_urlscan_params["dom"]["link"]
            )

            assert f"https://urlscan.io/result/{test_urlscan_params['uuid']}/" == actual["report"]
            assert test_urlscan_params["screenshot"]["path"] == await actual["screenshot"]
            assert test_urlscan_params["dom"]["path"] == await actual["dom"]


@pytest.mark.asyncio
async def test_download_screenshot(mocker, test_urlscan_params, screenshot_response):
    mock_save_file = mocker.patch("src.urlscanio.urlscan.UrlScan.save_file")
    mock_save_file.return_value = return_async(None)

    with aioresponses() as mocked:
        mocked.get(test_urlscan_params["screenshot"]["link"],
                   status=200,
                   body=screenshot_response)

        async with urlscan.UrlScan(api_key=test_urlscan_params["api_key"],
                                   data_dir=test_urlscan_params["data_dir"]) as url_scan:
            actual = await url_scan.download_screenshot(test_urlscan_params["screenshot"]["link"])
            assert str(test_urlscan_params["screenshot"]["path"]) == actual
            mock_save_file.assert_called_once_with(test_urlscan_params["screenshot"]["path"], screenshot_response)


@pytest.mark.asyncio
async def test_download_dom(mocker, test_urlscan_params, dom_response):
    mock_save_file = mocker.patch("src.urlscanio.urlscan.UrlScan.save_file")
    mock_save_file.return_value = return_async(None)

    with aioresponses() as mocked:
        mocked.get(test_urlscan_params["dom"]["link"],
                   status=200,
                   body=dom_response)

        async with urlscan.UrlScan(api_key=test_urlscan_params["api_key"],
                                   data_dir=test_urlscan_params["data_dir"]) as url_scan:
            actual = await url_scan.download_dom(test_urlscan_params["uuid"], test_urlscan_params["dom"]["link"])
            assert str(test_urlscan_params["dom"]["path"]) == actual
            mock_save_file.assert_called_once()
