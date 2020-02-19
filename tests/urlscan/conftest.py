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
        "result_url": "https://urlscan.io/api/v1/result/{test_uuid}".format(test_uuid=test_uuid),
        "data_dir": test_data_dir,
        "screenshot": {
            "link": "https://urlscan.io/screenshots/{test_uuid}.png".format(test_uuid=test_uuid),
            "path": test_data_dir.joinpath(
                "screenshots/{test_uuid}.png".format(test_uuid=test_uuid)
            )
        },
        "dom": {
            "link": "https://urlscan.io/dom/{test_uuid}/".format(test_uuid=test_uuid),
            "path": test_data_dir.joinpath(
                "doms/{test_uuid}.txt".format(test_uuid=test_uuid)
            )
        }
    }


@pytest.fixture
def submit_response():
    submit_resp_path = pathlib.Path(
        "{dir}/submit_api.json".format(dir=SAMPLE_RESPONSE_DIR)
    )
    with open(submit_resp_path, "r", encoding="utf-8") as res:
        return json.loads(res.read())


@pytest.fixture
def success_result_response():
    success_result_resp_path = pathlib.Path(
        "{dir}/result_api.json".format(dir=SAMPLE_RESPONSE_DIR)
    )
    with open(success_result_resp_path, "r", encoding="utf-8") as res:
        return json.loads(res.read())


@pytest.fixture
def not_found_result_response():
    not_found_result_resp_path = pathlib.Path(
        "{dir}/404_result_api.json".format(dir=SAMPLE_RESPONSE_DIR)
    )
    with open(not_found_result_resp_path, "r", encoding="utf-8") as res:
        return json.loads(res.read())


@pytest.fixture
def screenshot_response():
    img_bytes_io = BytesIO()
    img = Image.open(pathlib.Path("{dir}/screenshot.png".format(dir=SAMPLE_RESPONSE_DIR)))
    img.save(img_bytes_io, "PNG")
    img_bytes_io.seek(0)
    return img_bytes_io.read()


@pytest.fixture
def dom_response():
    dom_response_path = pathlib.Path(
        "{dir}/dom.txt".format(dir=SAMPLE_RESPONSE_DIR)
    )
    with open(dom_response_path, "r", encoding="utf-8") as res:
        return res.read()
