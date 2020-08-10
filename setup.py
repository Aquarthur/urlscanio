import setuptools

SETUP_REQUIRES = [
    "pytest-pylint",
    "pytest-runner",
    "wheel"
]

INSTALL_REQUIRES = [
    "aiohttp",
    "aiofiles"
]

TESTS_REQUIRES = [
    "Pillow",
    "pylint",
    "pytest",
    "pytest-asyncio",
    "pytest-mock",
    "aioresponses"
]

setuptools.setup(
    name="urlscanio",
    version="0.2.0",
    description=("Command line utility to get information about a website "
                 "using URLScan.io's APIs."),
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Aquarthur/urlscanio",
    author="Arthur Verkaik",
    author_email="art.v412@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython"
    ],
    python_requires=">=3.8",
    keywords="urlscan cli",
    packages=setuptools.find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    setup_requires=SETUP_REQUIRES,
    tests_require=TESTS_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    entry_points={
        "console_scripts": [
            "urlscanio = src.urlscanio.__main__:main"
        ]
    }
)
