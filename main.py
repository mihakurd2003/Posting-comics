import os
import random
import sys
import requests
from dotenv import load_dotenv
from urllib.parse import urljoin


def get_comics(url: str, filename):
    response_comics = requests.get(url=urljoin(url, f'{filename}/info.0.json'))
    response_comics.raise_for_status()

    response_img = requests.get(url=response_comics.json()['img'])
    response_img.raise_for_status()

    comment = response_comics.json()['alt']

    with open(f'{filename}.jpg', 'wb') as file:
        file.write(response_img.content)

    return comment


def get_upload_url(token, group_id, filename):
    headers = {'Authorization': f'Bearer {token}'}
    response_upload_server = requests.get(
        url='https://api.vk.com/method/photos.getWallUploadServer',
        params={'v': 5.131, 'group_id': group_id},
        headers=headers
    )

    with open(f'{filename}.jpg', 'rb') as file:
        upload_url = response_upload_server.json()['response']['upload_url']
        response_download = requests.post(url=upload_url, files={'photo': file})

    response_download.raise_for_status()

    os.remove(f'{filename}.jpg')

    return response_download


def save_photo(group_id, headers, response):
    response_saver = requests.post(
        url='https://api.vk.com/method/photos.saveWallPhoto',
        params={'v': 5.131,
                'group_id': group_id,
                'photo': response.json()['photo'],
                'server': response.json()['server'],
                'hash': response.json()['hash']
                },
        headers=headers
    )
    response_saver.raise_for_status()
    return response_saver


def posting_photo(group_id, headers, comment, response):
    attachments = f'photo{response.json()["response"][0]["owner_id"]}_{response.json()["response"][0]["id"]}'
    response_posting = requests.post(
        url='https://api.vk.com/method/wall.post',
        params={
            'v': 5.131, 'owner_id': f'-{group_id}',
            'attachments': attachments,
            'message': comment,
            'from_group': 1,
        },
        headers=headers,
    )
    response_posting.raise_for_status()


def main():
    load_dotenv()
    headers = {'Authorization': f"Bearer {os.environ['VK_TOKEN']}"}
    vk_token, vk_group_id = os.environ['VK_TOKEN'], os.environ['VK_GROUP_ID']
    comics_num = random.randint(0, 2733)

    try:
        comment = get_comics(url='https://xkcd.com/', filename=comics_num)
        response_download = get_upload_url(vk_token, vk_group_id, filename=comics_num)
        response_saver = save_photo(vk_group_id, headers, response_download)
        posting_photo(vk_group_id, headers, comment,  response_saver)

    except requests.exceptions.HTTPError:
        print(f'HTTP Error in {comics_num} comics', file=sys.stderr)
    except requests.exceptions.ConnectionError:
        print('Connection Error')


if __name__ == '__main__':
    main()
