from re import S, T
from typing import Dict, List
import socket
import argparse
import json
from data_structures import AvaliabilityResponse, CoordinatorResponse, ServerInfo, VideoDescriptor, VideoKey
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import requests


class Coordinator:
    def __init__(self) -> None:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [COORDINATOR] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        self._servers: Dict[ServerInfo, int] = {}
        self._movies: Dict[VideoKey, VideoDescriptor] = {}

        self.init_params()

        app = Flask(__name__)
        CORS(app)

        @app.route('/add_video/', methods=['POST'])
        def add_video():
            try:
                data = request.get_json()
                video_key = data['video_key']
                video_descriptor = data['video_descriptor']

                video_descriptor = VideoDescriptor(**video_descriptor)
                video_key = VideoKey(**video_key)
                self._movies[video_key] = video_descriptor
                print(self._movies)
                return jsonify({'success': True, 'message': 'Movie added successfully'}), 200
            except Exception as e:
                logging.info(e)
                return jsonify({'error': str(e)}), 400

        @app.route('/servers/', methods=['GET'])
        def get_servers():
            try:
                # Pobieranie parametrów z query string
                name = request.args.get('name')
                quality = request.args.get('quality')

                # Sprawdzenie, czy oba parametry są dostępne
                if not name or not quality:
                    return jsonify({'error': 'Missing parameters: name and quality'}), 400

                # Tutaj name i quality są dostępne jako zmienne w funkcji
                data = {'name': name, 'quality': int(quality)}
                logging.info(f'Dane: {data}')

                video_key, video_descriptor = self.extract_video_info(data)

                if not video_key in self._movies.keys():
                    return jsonify({'error': 'File not found.'}), 404

                if video_descriptor is None:
                    return jsonify({'error': 'File not found.'}), 404

                available_servers = self.find_available_servers(
                    video_descriptor)

                min_load = min([self._servers[server]
                               for server, location in available_servers])
                logging.info(f'min_load: {min_load}')

                available_servers = [
                    (server, location) for server, location in available_servers if self._servers[server] == min_load]

                for server, location in available_servers:
                    logging.info(f'{server}-{self._servers[server]}')

                # JEŚLI CHCEMY ZWRACAC JEDEN SERWER
                available_servers = available_servers[:2]
                for server, location in available_servers:
                    self._servers[server] += 1

                serialized_servers = [CoordinatorResponse(server.address, server.port, location).__dict__
                                      for server, location in available_servers]
                logging.info(jsonify(serialized_servers))

                return jsonify(serialized_servers)

            except Exception as e:
                logging.info(e)
                return jsonify({'error': str(e)}), 400
        self.app = app

    def extract_video_info(self, data):
        video_key = VideoKey(**data)
        video_descriptor = self._movies.get(video_key)
        return video_key, video_descriptor

    def find_available_servers(self, video_descriptor):
        serialized_data = json.dumps(video_descriptor.__dict__)
        available_servers = []

        for server in self._servers:
            url = f"http://{server.address}:{server.port}/availability/"
            headers = {'Content-Type': 'application/json'}
            try:
                response = self.check_server_availability(
                    url, serialized_data, headers)
                response = AvaliabilityResponse(**response.json())
                logging.info(f"Received response: {response}")

                if response.avaliable:
                    available_servers.append((server, response.location))
            except Exception as e:
                logging.info(e)

        return available_servers

    def check_server_availability(self, url, data, headers):
        return requests.post(url, data=data, headers=headers)

    def init_params(self) -> None:
        self._servers[ServerInfo("127.0.0.1", 5001)] = 0
        self._servers[ServerInfo("127.0.0.1", 5002)] = 0


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Your script description here.")
    parser.add_argument("--coordinator_host", default="127.0.0.1",
                        help="The host address to connect the coordinator.")
    parser.add_argument("--coordinator_port", type=int, default=12345,
                        help="The port number to connect the coordinator.")

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()

    coordinator_host = args.coordinator_host
    coordinator_port = args.coordinator_port
    coordinator = Coordinator()
    coordinator.app.run(coordinator_host, coordinator_port, debug=True)
