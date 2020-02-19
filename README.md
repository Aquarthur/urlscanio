# urlscanio

## Summary

[URLScan.io][urlscan-homepage] is a useful tool for scanning and obtaining information from potentially malicious websites. The creators of URLScan have very helpfully made an [API][urlscan-api] which can be used to add some automation to your workflow. `urlscanio` is a simple Python CLI utility which makes use of the aforementioned APIs to automate my own personal workflow when it comes to using URLScan.

## Requirements

`urlscanio` makes heavy usage of `aiohttp`, which requires Python >= 3.5.3. You will also need a [URLScan.io][urlscan-homepage] account and/or API key.

## Installation

If you have a compatible Python version installed, simply run (using `pip3` if necessary):

```bash
pip install urlscanio
```

## How to use

In this section, the different functions of the CLI are outlined. You may also use `urlscanio -h` or `urlscanio --help` for information within your terminal.

### API key and download directory

This tool requires an environment variable named `URLSCAN_API_KEY` containing your API key. Optionally, you may also set an environment variable called `URLSCAN_DATA_DIR` to specify where the screenshots and DOM should be downloaded. If not set, they will be downloaded in the directory you run `urlscanio` from.

It is recommended to use `.bashrc` or `.zshrc` for this. If using PowerShell, add `URLSCAN_API_KEY` and `URLSCAN_DATA_DIR` to your user profile.

### Investigate URL

Provided a URL (containing the protocol and domain at minimum), will request a scan and download the corresponding screenshot and DOM, as well as the report URL.

Examples:

```bash
urlscanio -i https://www.some-dodgy.website
urlscanio --investigate http://some-dodgy.website
```

### Submit scan request

Provided a URL (containing the protocol and domain at minimum), will request a scan and return the UUID generated. This can then be used to determine eg the screenshot location.

Examples:

```bash
urlscanio -s https://www.some-dodgy.website
urlscanio --submit http://some-dodgy.website
```

### Retrieve scan information

Provided the UUID linked to the scan in question, will query the API to download the screenshot and DOM from the report, as well as return the report URL.

```bash
urlscanio -r c5be1459-0a64-4751-bf25-8dd6d3c5742d
urlscanio --retrieve c5be1459-0a64-4751-bf25-8dd6d3c5742d
```

[urlscan-homepage]: https://urlscan.io
[urlscan-api]: https://urlscan.io/about-api
