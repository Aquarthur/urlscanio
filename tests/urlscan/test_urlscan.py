import pathlib
import uuid
from typing import Any, Dict

import mock
import responses

from ..context import urlscan


@responses.activate
def test_submit_scan_request(test_urlscan_params: Dict[str, Any],
                             submit_response: Dict[str, Any]) -> None:
    responses.add(responses.POST, test_urlscan_params["submit_url"],
                  json=submit_response, status=200)

    url_scan = urlscan.UrlScan(
        api_key=test_urlscan_params["api_key"],
        data_dir=test_urlscan_params["data_dir"]
    )

    output_uuid: uuid.UUID = url_scan.submit_scan_request("https://www.google.co.uk")

    assert output_uuid == uuid.UUID(submit_response["uuid"])


@mock.patch("urlscanio.urlscan.UrlScan.download_dom")
@mock.patch("urlscanio.urlscan.UrlScan.download_screenshot")
@responses.activate
def test_fetch_result(mock_dl_img,
                      mock_dl_dom,
                      test_urlscan_params: Dict[str, Any],
                      success_result_response: Dict[str, Any]) -> None:
    mock_dl_img.return_value = test_urlscan_params["screenshot"]["path"]
    mock_dl_dom.return_value = test_urlscan_params["dom"]["path"]
    responses.add(responses.GET, test_urlscan_params["result_url"],
                  json=success_result_response, status=200)

    url_scan = urlscan.UrlScan(
        api_key=test_urlscan_params["api_key"],
        data_dir=test_urlscan_params["data_dir"]
    )

    result: Dict[str, str] = url_scan.fetch_result(test_urlscan_params["uuid"])

    mock_dl_img.assert_called_once_with(test_urlscan_params["screenshot"]["link"])
    mock_dl_dom.assert_called_once_with(
        test_urlscan_params["uuid"],
        test_urlscan_params["dom"]["link"]
    )

    assert result["report"] == \
        "https://urlscan.io/result/{uuid}/".format(uuid=test_urlscan_params["uuid"])
    assert result["screenshot"] == mock_dl_img.return_value
    assert result["dom"] == mock_dl_dom.return_value


@mock.patch("PIL.PngImagePlugin.PngImageFile.save")
@mock.patch("PIL.Image.open")
@responses.activate
def test_download_screenshot(mock_pil_img_open,
                             mock_pil_img_save,
                             test_urlscan_params: Dict[str, Any],
                             screenshot_response: Any) -> None:
    mock_pil_img_save.return_value = None
    responses.add(responses.GET, test_urlscan_params["screenshot"]["link"],
                  body=screenshot_response, status=200)

    url_scan = urlscan.UrlScan(
        api_key=test_urlscan_params["api_key"],
        data_dir=test_urlscan_params["data_dir"]
    )

    screenshot_path: pathlib.Path = \
        url_scan.download_screenshot(test_urlscan_params["screenshot"]["link"])

    mock_pil_img_open.assert_called_once()
    assert screenshot_path == test_urlscan_params["screenshot"]["path"]


@mock.patch("builtins.open")
@mock.patch("builtins.print")
@responses.activate
def test_download_dom(mock_print,
                      mock_open,
                      test_urlscan_params: Dict[str, Any],
                      dom_response: Any) -> None:
    responses.add(responses.GET, test_urlscan_params["dom"]["link"],
                  body=dom_response, status=200)

    url_scan = urlscan.UrlScan(
        api_key=test_urlscan_params["api_key"],
        data_dir=test_urlscan_params["data_dir"]
    )

    dom_path: pathlib.Path = \
        url_scan.download_dom(test_urlscan_params["uuid"], test_urlscan_params["dom"]["link"])

    mock_open.assert_called_once_with(test_urlscan_params["dom"]["path"], "w")
    mock_print.assert_called_once_with(dom_response, file=mock_open().__enter__())
    assert dom_path == test_urlscan_params["dom"]["path"]
