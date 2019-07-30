import setuptools

SETUP_REQUIRES = [
    "pytest-pylint",
    "pytest-runner"
]

INSTALL_REQUIRES = [
    "pillow",
    "requests"
]

TESTS_REQUIRES = [
    "mock",
    "pylint",
    "pytest",
    "responses"
]

setuptools.setup(
    name="urlscanio",
    version="0.0.5",
    description=("Command line utility to get information about a website "
                 "using URLScan.io's APIs."),
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Aquarthur/urlscanio",
    author="Arthur Verkaik",
    author_email="art.v412@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython"
    ],
    keywords="urlscan cli",
    packages=setuptools.find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    setup_requires=SETUP_REQUIRES,
    tests_require=TESTS_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    entry_points={
        "console_scripts": [
            "urlscan = src.urlscanio.__main__:main"
        ]
    }
)
