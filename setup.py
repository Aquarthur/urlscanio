from glob import glob
from os.path import basename, splitext

import setuptools

setuptools.setup(
    name="urlscanio",
    version="0.0.1",
    description=("Command line utility to get information about a website "
                 "using URLScan.io's APIs."),
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    author="Arthur Verkaik",
    author_email="art.v412@gmail.com",
    url="",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython"
    ],
    setup_requires=["pytest-runner", "pytest-pylint"],
    tests_require=["pytest", "pylint"],
    install_requires=[
        "pillow",
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "urlscanio = urlscanio.__main__:main"
        ]
    }
)