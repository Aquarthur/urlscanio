import json
import pathlib
import uuid
from io import BytesIO

import pytest
from PIL import Image

SAMPLE_RESPONSE_DIR = pathlib.Path("tests/sample_responses").absolute()


@pytest.fixture
def test_urlscan_params():
    test_uuid = uuid.UUID("e2963e73-74e2-46d0-b9d4-db7db9d6b79d")
    test_data_dir = pathlib.Path(".")

    return {
        "api_key": "some-api-key",
        "uuid": test_uuid,
        "submit_url": "https://urlscan.io/api/v1/scan/",
        "result_url": f"https://urlscan.io/api/v1/result/{test_uuid}",
        "data_dir": test_data_dir,
        "screenshot": {
            "link": f"https://urlscan.io/screenshots/{test_uuid}.png",
            "path": test_data_dir.joinpath(f"screenshots/{test_uuid}.png")
        },
        "dom": {
            "link": f"https://urlscan.io/dom/{test_uuid}/",
            "path": test_data_dir.joinpath(f"doms/{test_uuid}.txt")
        }
    }


@pytest.fixture
def submit_response():
    submit_resp_path = pathlib.Path(f"{SAMPLE_RESPONSE_DIR}/submit_api.json")
    with open(submit_resp_path, "r", encoding="utf-8") as res:
        return json.loads(res.read())


@pytest.fixture
def success_result_response():
    success_result_resp_path = pathlib.Path(f"{SAMPLE_RESPONSE_DIR}/result_api.json")
    with open(success_result_resp_path, "r", encoding="utf-8") as res:
        return json.loads(res.read())


@pytest.fixture
def not_found_result_response():
    not_found_result_resp_path = pathlib.Path(f"{SAMPLE_RESPONSE_DIR}/404_result_api.json")
    with open(not_found_result_resp_path, "r", encoding="utf-8") as res:
        return json.loads(res.read())


@pytest.fixture
def screenshot_response():
    img_bytes_io = BytesIO()
    img = Image.open(pathlib.Path(f"{SAMPLE_RESPONSE_DIR}/screenshot.png"))
    img.save(img_bytes_io, "PNG")
    img_bytes_io.seek(0)
    return img_bytes_io.read()


@pytest.fixture
def dom_response():
    dom_response_path = pathlib.Path(f"{SAMPLE_RESPONSE_DIR}/dom.txt")
    with open(dom_response_path, "r", encoding="utf-8") as res:
        return res.read()
