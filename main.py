import requests
from dotenv import load_dotenv
import os
import random
import urllib.parse


def download_random_comic(api_xkcd_url):
    random_comic_number = random.randint(0, 2500)
    random_comic_url = api_xkcd_url.format(random_comic_number)
    xkcd_response = requests.get(random_comic_url)
    xkcd_response.raise_for_status()
    decoded_response = xkcd_response.json()
    random_comic_comment = decoded_response['alt']
    random_comic_img = decoded_response['img']
    file_extension = make_file_extension_from_link(random_comic_img)
    file_name = 'random_img{}'.format(file_extension)
    comic_response = requests.get(random_comic_img)
    comic_response.raise_for_status()
    with open(file_name, 'wb') as file:
        file.write(comic_response.content)
    return file_name, random_comic_comment


def make_file_extension_from_link(link):
    url_component = urllib.parse.urlparse(link).path
    url_clean_component = urllib.parse.unquote(url_component)
    file_extension = os.path.splitext(url_clean_component)[1]
    return file_extension


def get_vk_upload_url(vk_method_urls, payload):
    response = requests.get(
        vk_method_urls['get_wall_upload'],
        params=payload
    )
    response.raise_for_status()
    upload_url = response.json()['response']['upload_url']
    return upload_url


def upload_comics_to_vkserver(upload_url, file_name):
    with open(file_name, 'rb') as photo:
        upload_photo = {'photo': photo}
        send_photo_to_vk_server = requests.post(
            upload_url,
            files=upload_photo
        )
    send_photo_to_vk_server.raise_for_status()
    decoded_response = send_photo_to_vk_server.json()
    server = decoded_response['server']
    uploaded_photo = decoded_response['photo']
    photo_hash = decoded_response['hash']
    return server, uploaded_photo, photo_hash


def save_photo_to_vk_wall(vk_method_urls, payload):
    save_photo_on_wall = requests.post(
        vk_method_urls['save_wall_photo'],
        params=payload
    )
    decoded_response = save_photo_on_wall.json()
    media_id = decoded_response['response'][0]['id']
    owner_id = decoded_response['response'][0]['owner_id']
    return media_id, owner_id


def post_photo_to_vk_wall(vk_method_urls, payload):
    wall_post = requests.post(vk_method_urls['wall_post'], params=payload)
    wall_post.raise_for_status()
    return wall_post


def delete_img_file(file_name):
    os.remove(file_name)


if __name__ == '__main__':
    load_dotenv()
    vk_access_token = os.getenv("VK_ACCESS_TOKEN")
    vk_group_id = os.getenv("VK_GROUP_ID")
    api_xkcd_url = 'https://xkcd.com/{}/info.0.json'
    payload = {
        'access_token': vk_access_token,
        'v': '5.131'
    }
    vk_method_urls = {
        'save_wall_photo': 'https://api.vk.com/method/photos.saveWallPhoto',
        'get_wall_upload': 'https://api.vk.com/method/photos.getWallUploadServer',
        'wall_post': 'https://api.vk.com/method/wall.post'
    }

    try:
        file_name, comic_comment = download_random_comic(api_xkcd_url)
    except (requests.HTTPError, requests.ConnectionError) as e:
        exit('Не возможно получить данные с сервера:\n{}'.format(e))
    except (OSError, PermissionError) as e:
        exit('Ошибка:\n{}'.format(e))
    try:
        upload_url = get_vk_upload_url(vk_method_urls, payload)
        server, uploaded_photo, photo_hash = upload_comics_to_vkserver(
            upload_url,
            file_name
        )
        payload['hash'] = photo_hash
        payload['photo'] = uploaded_photo
        payload['server'] = server
        payload['message'] = comic_comment
        media_id, owner_id = save_photo_to_vk_wall(vk_method_urls, payload)
        payload['media_id'] = media_id
        payload['attachments'] = 'photo{}_{}'.format(owner_id, media_id)
        payload['owner_id'] = '-{}'.format(vk_group_id)
        wall_post = post_photo_to_vk_wall(vk_method_urls, payload)
        print("Комикс успешно опубликован!")
    except (requests.HTTPError, requests.ConnectionError) as e:
        exit('Не возможно получить данные с сервера:\n{}'.format(e))
    except (OSError, PermissionError, FileNotFoundError) as e:
        exit('Не возможно открыть файл:\n{}'.format(e))
    try:
        delete_img_file(file_name)
    except (OSError, PermissionError, FileNotFoundError) as e:
        print('Получили ошибку: {} '.format(e))
