from . import urlscan
from . import utils

import argparse
import os
import pathlib
import uuid
from typing import Dict, Optional

def __main__() -> None:
    parser: argparse.ArgumentParser = utils.create_arg_parser()
    args: argparse.Namespace = parser.parse_args()
    utils.validate_arguments(args)

    api_key: Optional[str] = os.getenv("URLSCAN_API_KEY", None)
    data_dir: pathlib.Path = pathlib.Path(os.getenv("URLSCAN_DATA_DIR", "."))
    utils.create_data_dir(data_dir)

    url_scan = urlscan.UrlScan(
        api_key=api_key,
        data_dir=data_dir
    )

    if args.investigate:
        result: Dict[str, str] = url_scan.investigate(args.investigate)
        print("\nScan report URL:\t\t{url}".format(url=result["report"]))
        print("Screenshot download location:\t{img}".format(img=result["screenshot"]))
        print("DOM download location:\t\t{dom}".format(dom=result["dom"]))

    elif args.retrieve:
        result: Dict[str, str] = url_scan.fetch_result(args.retrieve)
        print("\nScan report URL:\t\t{url}".format(url=result["report"]))
        print("Screenshot download location:\t{img}".format(img=result["screenshot"]))
        print("DOM download location:\t\t{dom}".format(dom=result["dom"]))

    elif args.submit:
        scan_uuid: uuid.UUID = url_scan.submit_scan_request(args.submit)
        print("\nScan UUID:\t\t{uuid}".format(uuid=scan_uuid))
