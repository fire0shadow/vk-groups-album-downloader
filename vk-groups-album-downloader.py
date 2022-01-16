import vk_api
from pathlib import Path
import requests
import os
import re
import argparse

parser = argparse.ArgumentParser(description='Fetch all photo albums in max resolution from VK.com group.')
parser.add_argument('login', help='Your VK.com login')
parser.add_argument('password', help='Your VK.com password')
parser.add_argument('id', help='VK.com group id for fetching photo albums')
parser.add_argument('--fetch-wall', help='Fetch photos from group wall', required=False, action='store_true')
parser.add_argument('--fetch-id', help='Fetch one album from group', required=False)

arguments = parser.parse_args()

LOGIN = arguments.login
PASSWORD = arguments.password
GROUPID = arguments.id
FETCH_WALL = arguments.fetch_wall
FETCH_ID = arguments.fetch_id

def auth_handler():
    key = input("Enter authentication code: ")
    remember_device = True

    return key, remember_device

def auth():
	try:
		vk_session = vk_api.VkApi(LOGIN, PASSWORD, auth_handler=auth_handler)
		vk_session.auth(token_only=True)
		return vk_session.get_api()
	except vk_api.exceptions.BadPassword:
		print("Wrong login or password")
		exit()

def fetch_albums(vk):
	try:
		return vk.photos.getAlbums(owner_id='-' + GROUPID)
	except:
		print("Something went wrong while fetching albums list. Maybe you don't have access to group albums?")
		exit()

def get_group_name(vk):
	try: 
		name = vk.groups.getById(group_id=GROUPID)[0]['name']

		if name == 'DELETED':
			exit()

		return name
	except:
		print("Something went wrong while fetching group name. Maybe your group doesn't exists or it's deleted?")
		exit()

def fetch_photos_from_album(vk, owner, id, offset = 0):
	return vk.photos.get(owner_id = owner, album_id = id, count = 1000, offset = offset)['items']

def fetch_all_photos_from_album(vk, owner, id):
	photos = []
	condition = True

	i = 0
	while condition:
		print('Processing album photos, downloaded data pack №' + str(i + 1))

		fetched = fetch_photos_from_album(vk, owner, id, 1000 * i)
		if len(fetched) != 1000:
			condition = False

		photos = photos + fetched
		i = i + 1

	print("Total images in album: " + str(len(photos)))
	return photos

def latest_file(path):
    files = sorted(Path(path).iterdir(), key=os.path.getctime)
    if len(files):
    	return files[-1].name.split('.')[0]
    
    return 0

def download_photos(photos, dirname):
	offset = 0

	if not os.path.exists(dirname):
		Path(dirname).mkdir(parents=True, exist_ok=True)
	else:
		latest = latest_file(dirname)

		if latest == len(photos):
			print('Album "' + album_name + '" already downloaded, skipping...')
			return
		else:
			offset = int(latest)

	y = 1 + offset
	for photo in photos[offset:]:
		print("Downloading image №" + str(y) + "...")

		previousWidth = 0
		sizeIndex = 0

		x = 0
		for size in photo['sizes']:
			if size['width'] > previousWidth:
				previousWidth = size['width']
				sizeIndex = x

			x = x + 1

		filename = dirname + "/" + str(y) + ".jpg"
		if os.path.exists(filename):
			os.remove(filename)

		img_data = requests.get(photo['sizes'][sizeIndex]['url']).content
		with open(filename, 'wb') as handler:
		    handler.write(img_data)

		y = y + 1

vk = auth()
ALBUMS_PATH = "albums/" + re.sub(r'[\\/*?:"<>|]', "", get_group_name(vk).replace("...", "").replace("/", "-")) + " [" + GROUPID + "]/"
albums = fetch_albums(vk)

if not os.path.exists(ALBUMS_PATH):
	Path(ALBUMS_PATH).mkdir(parents=True, exist_ok=True)

if FETCH_ID:
	for item in albums['items']:
		if int(item['id']) == int(FETCH_ID):
			album_name = re.sub(r'[\\/*?:"<>|]', "", item['title'].replace("...", "").replace("/", "-"))
			dirname = ALBUMS_PATH + album_name

			print("Fetching album data: " + album_name + "...")
			photos = fetch_all_photos_from_album(vk, item['owner_id'], item['id'])
			download_photos(photos, dirname)
else:
	if FETCH_WALL:
		wall_dirname = ALBUMS_PATH + 'Wall Photos'
		print("Fetching album data: Wall photos...")
		print("Processing wall album data, it may take some time...")
		download_photos(fetch_all_photos_from_album(vk, '-' + GROUPID, 'wall'), wall_dirname)

	for item in albums['items']:
		album_name = re.sub(r'[\\/*?:"<>|]', "", item['title'].replace("...", "").replace("/", "-"))
		dirname = ALBUMS_PATH + album_name

		print("Fetching album data: " + album_name + "...")
		photos = fetch_all_photos_from_album(vk, item['owner_id'], item['id'])
		download_photos(photos, dirname)

print("All albums downloaded, exiting application...")
