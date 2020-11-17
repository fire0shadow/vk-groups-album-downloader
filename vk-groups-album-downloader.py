import vk_api
from pathlib import Path
import requests
import os
import re

login = 'your login'
password = 'your password'

groupid = 'your group id'

vk_session = vk_api.VkApi(login, password)
vk_session.auth()

vk = vk_session.get_api()
albums = vk.photos.getAlbums(owner_id='-' + groupid)

if not os.path.exists("albums/"):
	Path("albums/").mkdir(parents=True, exist_ok=True)

i = 0
for item in albums['items']:
	album_name = re.sub(r'[\\/*?:"<>|]', "", item['title'].replace("...", "").replace("/", "-"))
	dirname = "albums/" + album_name

	if not os.path.exists(dirname):
		Path(dirname).mkdir(parents=True, exist_ok=True)
		print("Скачивается альбом: " + album_name + "...")
		photos = vk.photos.get(owner_id = item['owner_id'], album_id = item['id'])

		y = 1
		for photo in photos['items']:
			print("Скачивается изображение №" + str(y) + "...")

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
	else:
		print('Альбом "' + album_name + '" уже скачан, пропускаю...')

	i = i + 1
