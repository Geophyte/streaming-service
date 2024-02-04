import json
from flask import Flask, send_from_directory
from flask_cors import CORS
import argparse
import os
import argparse
import logging
from typing import Dict
from flask import Flask, jsonify, request
from flask_cors import CORS
from data_structures import VideoDescriptor, AvaliabilityResponse, VideoKey
import os
from requests import post
from utils import generate_hls, calculate_directory_hash, calculate_directory_size

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [SERVER] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


class Server:
    def __init__(self, coordinator_host: str, coordinator_port: int, server_id: int) -> None:
        self._coordinator_host: str = coordinator_host
        self._coordinator_port: int = coordinator_port
        self._server_id: int = server_id

        self._movies_location: Dict[VideoDescriptor, str] = {}

        app = Flask(__name__)
        CORS(app)

        @app.route('/availability/', methods=['POST'])
        def get_file_location():
            try:
                data = request.get_json()
                received_descriptor = VideoDescriptor(**data)
                logging.info(
                    f'Received descriptior: {received_descriptor}')
                if received_descriptor in self._movies_location:
                    video_location = self._movies_location[received_descriptor]
                    logging.info(
                        f"VideoDescriptor found in the coordinator's database. Location: {video_location}")

                    # Send a response to the coordinator indicating file presence
                    response_data = {"avaliable": True,
                                     "location": video_location}
                    response = AvaliabilityResponse(**response_data)
                    logging.info(f'Response: {jsonify(response)}')
                    return jsonify(response)
                return jsonify(AvaliabilityResponse(avaliable=False, location=None))
            except Exception as e:
                logging.warning(str(e))
                return jsonify({'error': str(e)}), 400

        @app.route('/add_movie/', methods=['POST'])
        def add_movie():
            try:
                data = request.get_json()
                video_path = data.pop('video_path')
                logging.info(video_path)

                video_key = VideoKey(**data)
                if not video_path:
                    return jsonify({'error': 'Missing video_path parameter'}), 400

                if not os.path.exists(video_path):
                    return jsonify({'error': 'File not found'}), 404

                hls_path = generate_hls(video_path, video_key.quality)

                hls_dir = os.path.dirname(hls_path)
                video_length = calculate_directory_size(hls_dir)
                video_hash = calculate_directory_hash(hls_dir)

                video_descriptor = VideoDescriptor(
                    video_hash, video_length)

                self._movies_location[video_descriptor] = hls_path

                logging.info(f'Movie added: {video_descriptor}')
                try:
                    url = f'http://{self._coordinator_host}:{self._coordinator_port}/add_video/'
                    data_to_send = {'video_key': video_key.__dict__,
                                    'video_descriptor': video_descriptor.__dict__}
                    headers = {'Content-Type': 'application/json'}
                    post(url, headers=headers, json=data_to_send)
                except Exception as e:
                    logging.warning(str(e))
                return jsonify({'success': True, 'message': 'Movie added successfully'}), 200

            except Exception as e:
                logging.warning(str(e))
                return jsonify({'error': str(e)}), 400

        @app.route('/<string:videoname>/<string:quality>/hls.m3u8')
        def hls_playlist(videoname, quality):
            file_dir = os.path.dirname(os.path.abspath(__file__))
            logging.info(file_dir)
            return send_from_directory(f'{file_dir}/static/{videoname}/{quality}', 'hls.m3u8')

        @app.route('/<string:videoname>/<string:quality>/<path:filename>')
        def hls_stream(videoname, quality, filename):
            file_dir = os.path.dirname(os.path.abspath(__file__))
            logging.info(file_dir)
            return send_from_directory(f'{file_dir}/static/{videoname}/{quality}', filename)

        self.app = app


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Your script description here.")
    parser.add_argument("--coordinator_host", default="127.0.0.1",
                        help="The host address to connect the coordinator.")
    parser.add_argument("--coordinator_port", type=int, default=12345,
                        help="The port number to connect the coordinator.")
    parser.add_argument("--server_host", default="127.0.0.1",
                        help="The host address to run the server.")
    parser.add_argument("--server_port", type=int, default=12345,
                        help="The port number to run the server.")
    parser.add_argument("--server_id", type=int, default=1,
                        help="The identifier of the server.")

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()

    coordinator_host = args.coordinator_host
    coordinator_port = args.coordinator_port
    server_host = args.server_host
    server_port = args.server_port
    server_id = args.server_id

    server = Server(coordinator_host, coordinator_port, server_id)
    server.app.run(server_host, server_port, debug=True)
