import requests


def add_movie(server_url, video_data):
    response = requests.post(f'{server_url}/add_movie/', json=video_data)

    if response.status_code == 200:
        print(f'Successfully added movie: {video_data}')
    else:
        print(f'Error adding movie: {video_data}')
        print(response.json())


if __name__ == '__main__':
    server_urls = 'http://127.0.0.1:5001', 'http://127.0.0.1:5002'

    video_data = {'video_path': 'media/video.mp4',
                  'name': 'rick roll',
                  'quality': 360}

    add_movie(server_urls[0], video_data)

    video_data = {'video_path': 'media/video.mp4',
                  'name': 'rick roll',
                  'quality': 720}

    add_movie(server_urls[1], video_data)

    video_data = {'video_path': 'media/video2.mp4',
                  'name': 'chlopaki nie placza',
                  'quality': 240}

    add_movie(server_urls[1], video_data)

    video_data = {'video_path': 'media/video.mp4',
                  'name': 'rick roll',
                  'quality': 360}
    
    add_movie(server_urls[1], video_data)
