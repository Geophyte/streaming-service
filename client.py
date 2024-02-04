import argparse
from data_structures import ServerInfo, VideoKey
import json
import socket
import logging
from datetime import datetime
import requests


class Client:
    def __init__(self, coordinator_host: str, coordinator_port: int, client_id: int) -> None:
        self._coordinator_host: str = coordinator_host
        self._coordinator_port: int = coordinator_port
        self._client_id: int = client_id

        # Create a logger with a custom format
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s [Client %(client_id)s] %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        self.logger = logging.getLogger(__name__)
        self.logger = logging.LoggerAdapter(
            self.logger, {'client_id': self._client_id})

    def run(self, video_name: str, video_quality: int) -> None:
        video_key: VideoKey = VideoKey(video_name, video_quality)
        serialized_data: str = json.dumps(video_key.__dict__)

        # Send request to /servers/ endpoint
        self.send_request(serialized_data)

    def send_request(self, data: str) -> None:
        url = f"http://{self._coordinator_host}:{self._coordinator_port}/servers/?name={video_name}&quality={video_quality}"
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                self.logger.info("Request successfully sent to /servers/")
                self.logger.info(response.json())
            else:
                self.logger.error(
                    f"Failed to send request. Status code: {response.status_code}")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed with error: {e}")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Your script description here.")
    parser.add_argument("--coordinator_host", default="127.0.0.1",
                        help="The host address to connect the coordinator.")
    parser.add_argument("--coordinator_port", type=int, default=5000,
                        help="The port number to connect the coordinator.")
    parser.add_argument('--video_name', type=str, default='video',
                        help="The name of video you want to see.")
    parser.add_argument('--video_quality', type=int, default=720,
                        help="The quality of video you want to see.")
    parser.add_argument('--client_id', type=int, default=1,
                        help="The identifier of the client.")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    coordinator_host = args.coordinator_host
    coordinator_port = args.coordinator_port
    video_name = args.video_name
    video_quality = args.video_quality
    client_id = args.client_id

    client = Client(coordinator_host, coordinator_port, client_id)
    client.run(video_name, video_quality)
