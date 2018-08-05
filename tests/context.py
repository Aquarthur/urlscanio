# pylint: disable=C0413,W0611
import pathlib
import sys

TEST_DIR: pathlib.Path = pathlib.Path.cwd().absolute()
PROJECT_DIR: pathlib.Path = pathlib.Path.cwd().parent.joinpath("src").absolute()

sys.path.insert(0, str(PROJECT_DIR))

from src.urlscanio import urlscan   # type: ignore
from src.urlscanio import utils     # type: ignore
