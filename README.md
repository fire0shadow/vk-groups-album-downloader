# VK Groups Album Downloader
A Python3 script using VK API for grabbing and downloading all group's photo albums

## Usage

'''
usage: vk-groups-album-downloader.py [-h] [--fetch-wall] login password id

Fetch all photo albums in max resolution from VK.com group.

positional arguments:
  login         Your VK.com login
  password      Your VK.com password
  id            VK.com group id for fetching photo albums

optional arguments:
  -h, --help    show this help message and exit
  --fetch-wall  Fetch photos from group wall
'''

## Dependencies

vk_api packet: https://pypi.org/project/vk-api/

You can install it via **pip**:
```
pip install vk-api
```
