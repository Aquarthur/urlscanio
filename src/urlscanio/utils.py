import argparse
import pathlib
import re
import urllib.parse
from typing import List, Pattern


def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="urlscan",
        description=(
            "Call URLScan.io's submission and result APIs to get information about "
            "a website. This tool requires an environment variable named "
            "URLSCAN_API_KEY to be set to your API key.\nOptionally, you may also set "
            "an environment variable called URLSCAN_DATA_DIR to specify where the "
            "screenshots and DOM should be downloaded. If not set, they will be downloaded "
            "in your current directory."
        ),
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-i", "--investigate",
        help=(
            "Investigate the specified URL. Returns the report URL and the locations of the "
            "DOM and screenshots."
        ),
        type=str
    )
    group.add_argument(
        "-s", "--submit",
        help="Submit a scan request for the specified URL. Returns the corresponding UUID.",
        type=str
    )
    group.add_argument(
        "-r", "--retrieve",
        help=(
            "Retrieves the scan report for the provided UUID. Returns the report URL and the "
            "download locations for the DOM and screenshot."
        ),
        type=str
    )

    return parser


def is_url_valid(url: str) -> bool:
    minimum_url_attributes: List[str] = ["scheme", "netloc"]
    token = urllib.parse.urlparse(url)
    return all([getattr(token, attribute) for attribute in minimum_url_attributes]) and \
           len([s for s in token.netloc.split(".") if s != ""]) > 1


def validate_arguments(args: argparse.Namespace) -> None:
    uuid_validator: Pattern = re.compile(
        "^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$"
    )

    if (args.investigate and not is_url_valid(args.investigate)) or \
       (args.submit and not is_url_valid(args.submit)):
        raise ValueError(
            "The URL provided does not contain the scheme (e.g. http:// or https://) "
            "and/or a non-empty location (e.g. google.com)"
        )
    elif args.retrieve and not bool(uuid_validator.match(args.retrieve)):
        raise ValueError("The UUID provided is incorrectly formatted")


def create_data_dir(data_dir: pathlib.Path) -> None:
    pathlib.Path("{data_dir}/screenshots".format(data_dir=data_dir)).mkdir(exist_ok=True)
    pathlib.Path("{data_dir}/doms".format(data_dir=data_dir)).mkdir(exist_ok=True)
