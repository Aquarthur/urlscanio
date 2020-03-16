import asyncio
import os
import platform
from pathlib import Path

from . import urlscan, utils


def main():
    parser = utils.create_arg_parser()
    args = parser.parse_args()
    utils.validate_arguments(args)

    api_key = os.environ["URLSCAN_API_KEY"]
    data_dir = Path(os.getenv("URLSCAN_DATA_DIR", "."))
    log_level = utils.convert_int_to_logging_level(args.verbose)

    utils.create_data_dir(data_dir)

    # See https://github.com/iojw/socialscan/issues/13
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(policy=asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(execute(args, api_key, data_dir, log_level))

async def execute(args, api_key, data_dir, log_level):
    async with urlscan.UrlScan(api_key=api_key, data_dir=data_dir, log_level=log_level) as url_scan:
        if args.investigate:
            investigation_result = await url_scan.investigate(args.investigate, args.private)
            print(f"\nScan report URL:\t\t{investigation_result['report']}")
            print(f"Screenshot download location:\t{investigation_result['screenshot']}")
            print(f"DOM download location:\t\t{investigation_result['dom']}\n")

        elif args.retrieve:
            retrieve_result = await url_scan.fetch_result(args.retrieve)
            print(f"\nScan report URL:\t\t{retrieve_result['report']}")
            print(f"Screenshot download location:\t{retrieve_result['screenshot']}")
            print(f"DOM download location:\t\t{retrieve_result['dom']}\n")

        elif args.submit:
            scan_uuid = await url_scan.submit_scan_request(args.submit, args.private)
            print(f"\nScan UUID:\t\t{scan_uuid}\n")
