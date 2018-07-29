import argparse
import os
import pathlib
import uuid
from typing import Dict, Union

from . import urlscan
from . import utils


def main() -> None:
    parser: argparse.ArgumentParser = utils.create_arg_parser()
    args: argparse.Namespace = parser.parse_args()
    utils.validate_arguments(args)

    api_key: str = os.environ["URLSCAN_API_KEY"]
    data_dir: pathlib.Path = pathlib.Path(os.getenv("URLSCAN_DATA_DIR", "."))
    utils.create_data_dir(data_dir)

    url_scan = urlscan.UrlScan(
        api_key=api_key,
        data_dir=data_dir
    )

    if args.investigate:
        investigation_result: Dict[str, Union[str, pathlib.Path]] = \
            url_scan.investigate(args.investigate)
        print("\nScan report URL:\t\t{url}".format(url=investigation_result["report"]))
        print("Screenshot download location:\t{img}".format(img=investigation_result["screenshot"]))
        print("DOM download location:\t\t{dom}".format(dom=investigation_result["dom"]))

    elif args.retrieve:
        retrieve_result: Dict[str, Union[str, pathlib.Path]] = url_scan.fetch_result(args.retrieve)
        print("\nScan report URL:\t\t{url}".format(url=retrieve_result["report"]))
        print("Screenshot download location:\t{img}".format(img=retrieve_result["screenshot"]))
        print("DOM download location:\t\t{dom}".format(dom=retrieve_result["dom"]))

    elif args.submit:
        scan_uuid: uuid.UUID = url_scan.submit_scan_request(args.submit)
        print("\nScan UUID:\t\t{uuid}".format(uuid=scan_uuid))
