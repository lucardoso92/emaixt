<h1 align="center"><b>EMAIXT<b></h1>
<p align="center"><b>The tool that extracts emails from a web page.</b></p>

## Example
![img](https://github.com/uxcardoso/emaixt/blob/master/img/screen.png?raw=false)

## Installation
```console
pip3 install -r requirements.txt
```

## Usage
```console
python3 emailxt.py -h
```
This will display help for the tool. Here are all the switches it supports.

```console
usage: emaixt.py [-h] [-s | --silent | --no-silent] [-p | --pipe | --no-pipe] -u URL

OPTIONS:
  -h, --help            show this help message and exit
  -s, --silent, --no-silent
                        Enable the silent mode
  -p, --pipe, --no-pipe
                        Enable the pipe mode
  -u URL, --url URL     URL to enumerate emails

Example: python emaixt.py -u https://www.example.com/contact
```

## Running EMAIXT

### URL Input
```console
python3 emaixt.py -u https://www.tesla.com/contact
```
### STDIN (piped) Input
```console
echo https://www.tesla.com/contact | python3 emaixt.py
```
```console
cat urls.py | python3 emaixt.py
```