# urlscanio
## Summary
[URLScan.io][urlscan-homepage] is a useful tool for scanning and obtaining information from potentially malicious websites. The creators of URLScan have very helpfully made an [API][urlscan-api] which can be used to add some automation to your workflow. `urlscanio` is a simple Python CLI utility which makes use of the aforementioned APIs to automate my own personal workflow when it comes to using URLScan.

## Requirements
`urlscanio` was written in Python 3.7 and currently requires the user to have Python >= 3.5, mostly due to the fact that it makes use of the `typing` module.


## Installation
If you have a compatible Python version installed, simply run (using `pip3` if necessary):

```bash
pip install urlscanio
```

## How to use
In this section, the different functions of the CLI are outlined. You may also use `urlscanio -h|--help` for information within your terminal.

### API key and download directory
This tool requires an environment variable named `URLSCAN_API_KEY` to be set to your API key. Optionally, you may also set an environment variable called `URLSCAN_DATA_DIR` to specify where the screenshots and DOM should be downloaded. If not set, they will be downloaded in the directory you run the script from.

It is recommended to use the `.bashrc` or `.zshrc` file for this. If using PowerShell, add the environment variables to your user profile.

### Investigate URL
Provided a URL (containing the protocol and domain at minimum), will request a scan and download the corresponding screenshot and DOM, as well as the report URL.

Examples:

```bash
urlscan -i https://www.amazon.co.uk
urlscan --investigate http://some-dodgy.website
```

### Submit scan request
Provided a URL (containing the protocol and domain at minimum), will request a scan and return the UUID generated. This can then be used to determine eg the screenshot location.

Examples:

```bash
urlscan -s https://www.amazon.co.uk
urlscan --submit http://some-dodgy.website
```

### Retrieve scan information
Provided the UUID linked to the scan in question, will query the API to download the screenshot and DOM from the report, as well as return the report URL.

```bash
urlscan -r c5be1459-0a64-4751-bf25-8dd6d3c5742d
urlscan --retrieve c5be1459-0a64-4751-bf25-8dd6d3c5742d
```

[urlscan-homepage]: https://urlscan.io
[urlscan-api]: https://urlscan.io/about-api/