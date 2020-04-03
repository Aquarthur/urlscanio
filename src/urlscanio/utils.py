import argparse
import logging
import pathlib
import re
import urllib.parse

def create_arg_parser():
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
    parser.add_argument(
        "-v", "--verbose",
        help=(
            "Determines how verbose the output of the command will be. There are three "
            "possible values: 0 (critical), 1 (info), and 2 (debug). The default value "
            "is set to 0 when no verbose flag is present. If a flag is added with no "
            "value specified, it is set to 1. Otherwise, it will simply use the value "
            "specified."
        ),
        choices=[0, 1, 2], default=0, nargs="?", const=1,
        type=int
    )

    parser.add_argument(
        "-p", "--private",
        help=("Submit the URL in private. Private searches are not shared with other users."),
        action="store_true"
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


def is_url_valid(url):
    minimum_url_attributes = ["scheme", "netloc"]
    token = urllib.parse.urlparse(url)
    return all([getattr(token, attribute) for attribute in minimum_url_attributes]) and \
           len([s for s in token.netloc.split(".") if s != ""]) > 1


def validate_arguments(args):
    uuid_validator = re.compile(
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


def create_data_dir(data_dir):
    pathlib.Path(f"{data_dir}/screenshots").mkdir(exist_ok=True)
    pathlib.Path(f"{data_dir}/doms").mkdir(exist_ok=True)

def convert_int_to_logging_level(log_level):
    mapping = {
        0: logging.CRITICAL,
        1: logging.INFO,
        2: logging.DEBUG
    }
    return mapping[log_level]
