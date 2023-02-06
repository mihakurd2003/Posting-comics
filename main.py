import os
import random
import sys
import requests
from dotenv import load_dotenv
from urllib.parse import urljoin
import traceback


class VkApiError(requests.HTTPError):
    """HTTP Error from vk response"""
    pass


def raise_vk_response(response):
    error_response = response.json()
    if 'error' in error_response:
        raise VkApiError(error_response['error']['error_msg'])


def get_comic(url: str, filename):
    comic_response = requests.get(url=urljoin(url, f'{filename}/info.0.json'))
    comic_response.raise_for_status()

    image_response = requests.get(url=comic_response.json()['img'])
    image_response.raise_for_status()

    comment = comic_response.json()['alt']

    with open(f'{filename}.jpg', 'wb') as file:
        file.write(image_response.content)

    return comment


def download_comic(token, group_id, filename):
    headers = {'Authorization': f'Bearer {token}'}
    upload_server_response = requests.get(
        url='https://api.vk.com/method/photos.getWallUploadServer',
        params={'v': 5.131, 'group_id': group_id},
        headers=headers,
    )
    upload_server_response.raise_for_status()
    raise_vk_response(upload_server_response)

    with open(f'{filename}.jpg', 'rb') as file:
        upload_url = upload_server_response.json()['response']['upload_url']
        upload_response = requests.post(url=upload_url, files={'photo': file})

    upload_response.raise_for_status()
    raise_vk_response(upload_response)

    return upload_response


def save_photo(group_id, token, response):
    response = response.json()
    headers = {'Authorization': f'Bearer {token}'}
    saving_comic_response = requests.post(
        url='https://api.vk.com/method/photos.saveWallPhoto',
        params={'v': 5.131,
                'group_id': group_id,
                'photo': response['photo'],
                'server': response['server'],
                'hash': response['hash']
                },
        headers=headers,
    )
    saving_comic_response.raise_for_status()
    raise_vk_response(saving_comic_response)
    return saving_comic_response


def post_photo(group_id, token, comment, response):
    response = response.json()
    headers = {'Authorization': f'Bearer {token}'}
    attachments = f'photo{response["response"][0]["owner_id"]}_{response["response"][0]["id"]}'
    posting_comic_response = requests.post(
        url='https://api.vk.com/method/wall.post',
        params={
            'v': 5.131, 'owner_id': f'-{group_id}',
            'attachments': attachments,
            'message': comment,
            'from_group': 1,
        },
        headers=headers,
    )
    posting_comic_response.raise_for_status()
    raise_vk_response(posting_comic_response)


def main():
    load_dotenv()
    vk_token, vk_group_id, last_comic_num = os.environ['VK_TOKEN'], os.environ['VK_GROUP_ID'], 2733
    comic_num = random.randint(0, last_comic_num)

    try:
        comment = get_comic(url='https://xkcd.com/', filename=comic_num)
        upload_response = download_comic(vk_token, vk_group_id, filename=comic_num)
        saving_comic_response = save_photo(vk_group_id, vk_token, upload_response)
        post_photo(vk_group_id, vk_token, comment, saving_comic_response)

    except VkApiError:
        print(traceback.format_exc(), file=sys.stderr)
    except requests.exceptions.HTTPError:
        print(traceback.format_exc(), file=sys.stderr)
    except requests.exceptions.ConnectionError:
        print(traceback.format_exc(), file=sys.stderr)
    finally:
        os.remove(f'{comic_num}.jpg')


if __name__ == '__main__':
    main()

