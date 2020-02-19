import argparse
import asyncio
import os
import platform
from pathlib import Path
import uuid
from typing import Dict, Union

from . import urlscan
from . import utils


def main():
    parser: argparse.ArgumentParser = utils.create_arg_parser()
    args: argparse.Namespace = parser.parse_args()
    utils.validate_arguments(args)

    api_key: str = os.environ["URLSCAN_API_KEY"]
    data_dir: Path = Path(os.getenv("URLSCAN_DATA_DIR", "."))
    utils.create_data_dir(data_dir)

    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(policy=asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(execute(args, api_key, data_dir))

async def execute(args, api_key, data_dir) -> None:
    async with urlscan.UrlScan(api_key=api_key, data_dir=data_dir) as url_scan:
        if args.investigate:
            investigation_result: Dict[str, Union[str, Path]] = \
                await url_scan.investigate(args.investigate)
            print(f"\nScan report URL:\t\t{investigation_result['report']}")
            print(f"Screenshot download location:\t{investigation_result['screenshot']}")
            print(f"DOM download location:\t\t{investigation_result['dom']}\n")

        elif args.retrieve:
            retrieve_result: Dict[str, Union[str, Path]] = \
                await url_scan.fetch_result(args.retrieve)
            print(f"\nScan report URL:\t\t{retrieve_result['report']}")
            print(f"Screenshot download location:\t{retrieve_result['screenshot']}")
            print(f"DOM download location:\t\t{retrieve_result['dom']}\n")

        elif args.submit:
            scan_uuid: uuid.UUID = await url_scan.submit_scan_request(args.submit)
            print(f"\nScan UUID:\t\t{scan_uuid}\n")
