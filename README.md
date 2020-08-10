# urlscanio

## Summary

[URLScan.io][urlscan-homepage] is a useful tool for scanning and obtaining information from potentially malicious websites. The creators of URLScan have very helpfully made an [API][urlscan-api] which can be used to add some automation to your workflow. `urlscanio` is a simple Python CLI utility which makes use of the aforementioned APIs to automate my own personal workflow when it comes to using URLScan.

## Requirements

`urlscanio` requires Python >= 3.8. You will also need a [URLScan.io][urlscan-homepage] account and/or API key.

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

### Proxy settings

`urlscanio` will use the proxy settings specified by the `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY` environment variables if present.

### Investigate URL

Provided a URL (containing the protocol and domain at minimum), will request a scan and download the corresponding screenshot and DOM, as well as the report URL.

```sh
urlscanio -i https://www.some-dodgy.website
urlscanio --investigate http://some-dodgy.website
```

### Submit scan request

Provided a URL (containing the protocol and domain at minimum), will request a scan and return the UUID generated. This can then be used to determine eg the screenshot location.

```sh
urlscanio -s https://www.some-dodgy.website
urlscanio --submit http://some-dodgy.website
```

### Retrieve scan information

Provided the UUID linked to the scan in question, will query the API to download the screenshot and DOM from the report, as well as return the report URL.

```sh
urlscanio -r c5be1459-0a64-4751-bf25-8dd6d3c5742d
urlscanio --retrieve c5be1459-0a64-4751-bf25-8dd6d3c5742d
```

### Batch Investigations

If you have >1 URL you'd like to investigate, use the `-b/--batch-investigate` flag. You will need a file containing a URL per line, eg:

```txt
https://www.example1.com
https://www.example2.com
https://www.example3.com
```

The filename containing the URLs can then be passed, triggering an "investigation" for each URL. It will trigger each investigation in 3 second intervals by default, as UrlScan.io requires a minimum of 2 seconds between scan requests.

`urlscanio` will produce an output CSV containing the results. The output CSV will be named `[input_stem].csv`; for example, passing in `test.txt` will produce `test.csv`.

```sh
urlscanio -b test.txt
urlscanio --batch-investigate test.txt
```

### Verbose mode

`urlscanio` includes a verbosity flag which takes 3 possible values: 0 (critical), 1 (info), and 2 (debug). This can be used with of the above commands to produce varying amounts of
logs to give context to the commands run. If the flag is not passed, the verbosity is set to 0. If the flag is passed without a value, the verbosity level is set to one.

```sh
urlscanio -i https://www.some-dodgy.website         # verbosity is 0 (critical)
urlscanio -v -i https://www.some-dodgy.website      # verbosity is 1 (info)
urlscanio -v 0 -i https://www.some-dodgy.website    # verbosity is 0 (critical)
urlscanio -v 1 -i https://www.some-dodgy.website    # verbosity is 1 (info)
urlscanio -v 2 -i https://www.some-dodgy.website    # verbosity is 2 (debug)
```

[urlscan-homepage]: https://urlscan.io
[urlscan-api]: https://urlscan.io/about-api
