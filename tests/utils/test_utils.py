import itertools
import uuid

import pytest

from ..context import utils

TEST_WEBSITE = "https://www.google.com"
TEST_UUID = uuid.uuid4()

TEST_FLAGS = {
    "investigate": f"-i {TEST_WEBSITE}",
    "submit": f"-s {TEST_WEBSITE}",
    "retrieve": f"-r {TEST_UUID}"
}

ALL_FLAG_COMBOS = \
    [combo for i in range(len(TEST_FLAGS) + 1)
     for combo in itertools.combinations(TEST_FLAGS.values(), i)]

ALL_SPLIT_FLAG_COMBOS = []
for combo in ALL_FLAG_COMBOS:
    split_flags = []
    for flag in combo:
        split_flags += flag.split(" ")
    ALL_SPLIT_FLAG_COMBOS.append(split_flags)

# Append scenario in which only verbose flag is presented
ALL_SPLIT_FLAG_COMBOS.append(["-v"])

@pytest.mark.parametrize("mock_flags", ALL_SPLIT_FLAG_COMBOS)
def test_create_arg_parser(mock_flags):
    parser = utils.create_arg_parser()
    print(mock_flags)
    if " ".join(mock_flags) in TEST_FLAGS.values():
        args = vars(parser.parse_args(mock_flags))
        for name, value in args.items():
            if name != "verbose" and args[name] is not None:
                assert TEST_FLAGS[name].split(" ")[1].strip() == \
                       value.strip()
    else:
        with pytest.raises(SystemExit):
            parser.parse_args(mock_flags)

MOCK_INVALID_VERBOSITY_LEVELS = (
    -1,
    3,
    10000,
    0.5,
    "a",
    'a',
    ["some", "list"],
    ("some", "tuple"),
)

@pytest.mark.parametrize("mock_invalid_verbosity_level", MOCK_INVALID_VERBOSITY_LEVELS)
def test_create_arg_parser_fails_with_invalid_verbosity_level(mock_invalid_verbosity_level):
    parser = utils.create_arg_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["-v", str(mock_invalid_verbosity_level), "-i", TEST_WEBSITE])

MOCK_INVALID_URLS = (
    "google.com",
    "www.google.com",
    "google",
    "https://google",
    "https://google.",
    "https://.google",
    "https://....google...."
)


@pytest.mark.parametrize("mock_invalid_url", MOCK_INVALID_URLS)
def test_is_url_valid_for_invalid_urls(mock_invalid_url):          # pylint: disable=C0103
    assert not utils.is_url_valid(mock_invalid_url)


@pytest.mark.parametrize("mock_flag", TEST_FLAGS.values())
def test_validate_arguments_with_valid_arguments(mock_flag):       # pylint: disable=C0103
    parser = utils.create_arg_parser()
    args = parser.parse_args(mock_flag.split(" "))
    utils.validate_arguments(args)
