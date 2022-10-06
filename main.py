import requests
from dotenv import load_dotenv
import os
import random
import urllib.parse


def download_random_comic():
    api_xkcd_url = 'https://xkcd.com/{}/info.0.json'
    last_comic_num_response = requests.get(api_xkcd_url.format(''))
    last_comic_num_response.raise_for_status()
    last_comic_num = last_comic_num_response.json()['num']
    random_comic_number = random.randint(0, last_comic_num)
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


def get_vk_upload_url(vk_access_token, api_version):
    api_vk_url = 'https://api.vk.com/method/photos.getWallUploadServer'
    response = requests.get(api_vk_url, params={
        'access_token': vk_access_token,
        'v': api_version
    })
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


def save_photo_to_vk_wall(
        vk_access_token,
        api_version,
        uploaded_photo,
        server,
        photo_hash
):
    api_vk_url = 'https://api.vk.com/method/photos.saveWallPhoto'
    save_photo_on_wall = requests.post(api_vk_url, params={
        'access_token': vk_access_token,
        'v': api_version,
        'photo': uploaded_photo,
        'server': server,
        'hash': photo_hash
    })
    decoded_response = save_photo_on_wall.json()
    media_id = decoded_response['response'][0]['id']
    owner_id = decoded_response['response'][0]['owner_id']
    return media_id, owner_id


def post_photo_to_vk_wall(
        access_token,
        api_version,
        group_id,
        message,
        attachment):
    api_vk_url = 'https://api.vk.com/method/wall.post'
    wall_post = requests.post(api_vk_url, params={
        'access_token': access_token,
        'v': api_version,
        'owner_id': -group_id,
        'message': message,
        'attachments': attachment,
    })
    wall_post.raise_for_status()
    return wall_post


if __name__ == '__main__':
    load_dotenv()
    api_version = 5.131
    vk_access_token = os.getenv("VK_ACCESS_TOKEN")
    vk_group_id = int(os.getenv("VK_GROUP_ID"))
    try:
        file_name, comic_comment = download_random_comic()
    except (requests.HTTPError, requests.ConnectionError) as e:
        exit('Не возможно получить данные с сервера:\n{}'.format(e))
    except (OSError, PermissionError) as e:
        exit('Ошибка:\n{}'.format(e))
    try:
        upload_url = get_vk_upload_url(vk_access_token, api_version)
        server, uploaded_photo, photo_hash = upload_comics_to_vkserver(
            upload_url,
            file_name
        )
        media_id, owner_id = save_photo_to_vk_wall(
            vk_access_token,
            api_version,
            uploaded_photo,
            server,
            photo_hash)
        attachment = 'photo{}_{}'.format(owner_id, media_id)
        wall_post = post_photo_to_vk_wall(
            vk_access_token,
            api_version,
            vk_group_id,
            comic_comment,
            attachment
        )
        print("Комикс успешно опубликован!")
    except (requests.HTTPError, requests.ConnectionError) as e:
        exit('Не возможно получить данные с сервера:\n{}'.format(e))
    except (OSError, PermissionError, FileNotFoundError) as e:
        exit('Не возможно открыть файл:\n{}'.format(e))
    finally:
        try:
            os.remove(file_name)
        except (OSError, PermissionError, FileNotFoundError) as e:
            exit('Ошибка:\n{}'.format(e))

