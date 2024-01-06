import logging
import os
import re
import subprocess
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


@dataclass
class VimeoDownloadInfo:
    id: str
    video_url: str
    audio_url: str
    audio_bitrate: int

    @staticmethod
    def from_master_json(master_json, master_json_url):
        clip_id = master_json["clip_id"]
        clip_id_url = f"/{clip_id}"
        index = master_json_url.find(clip_id_url)
        base_url = master_json_url[: index + len(clip_id_url)] + "/parcel/"

        heights = [(i, d["height"]) for (i, d) in enumerate(master_json["video"])]
        index = min(heights, key=lambda x: x[1])[0]
        video_url = base_url + master_json["video"][index]["base_url"]

        bitrate = [(i, d["bitrate"]) for (i, d) in enumerate(master_json["audio"])]
        index, min_bitrate = min(bitrate, key=lambda x: x[1])
        audio_url = base_url + master_json["audio"][index]["base_url"]

        return VimeoDownloadInfo(clip_id, video_url, audio_url, min_bitrate)


class EmbeddedVimeo:
    def _write_file(self, filepath, url):
        if os.path.exists(filepath):
            raise RuntimeError(f"Temporary file already exists {filepath}")

        with open(filepath, "wb") as file:
            logging.debug(f"Downloading {url} to {filepath}")
            resp = requests.get(url, stream=True)
            if resp.status_code != 200:
                raise RuntimeError(f"Unexpected status {resp.status_code} for {url}")
            for chunk in resp:
                file.write(chunk)

    def _find_player_config_json(self, html):
        soup = BeautifulSoup(html, "html.parser")
        title = soup.find_all("title")
        if title and title[0].string == "Sorry":
            raise RuntimeError(f"Privacy error when accessing video for")
        else:
            scripts = soup.find_all("script")
            player_config_pattern = re.compile(
                r"\s*window\.playerConfig\s*=\s*(.*)", re.DOTALL
            )
            player_config_match = None
            for script in scripts:
                if script.string:
                    player_config_match = player_config_pattern.search(script.string)
                    if player_config_match:
                        logging.debug("Found playerConfig match in script")
                        return player_config_match.group(1)
            if player_config_match is None:
                raise RuntimeError(f"window.playerConfig not found in response for")

    def _find_master_json_url(self, player_config_json):
        master_json_url_pattern = re.compile(r'"url":\s*"([^"]+)"')
        master_json_url_match = master_json_url_pattern.search(player_config_json)
        if master_json_url_match:
            master_json_url = master_json_url_match.group(1)
            logging.debug(f"Found url {master_json_url} match in playerConfig JSON")
            return master_json_url
        else:
            raise RuntimeError(f"Master JSON URL not foung in player config JSON")

    def _get_vimeo_download_info(self, master_json_url):
        logging.debug(f"Getting Master JSON URL {master_json_url}")
        response = requests.get(master_json_url)
        if response.status_code != 200:
            raise RuntimeError(f"Master JSON URL response {response.status_code}")
        download_info = VimeoDownloadInfo.from_master_json(
            response.json(), master_json_url
        )
        return download_info

    def _download(self, output_file, download_info):
        filename_video = f"temp_video_{download_info.id}.mp4"
        filename_audio = f"temp_audio_{download_info.id}.m4a"

        self._write_file(filename_video, download_info.video_url)
        self._write_file(filename_audio, download_info.audio_url)

        subprocess.call(
            f"ffmpeg -i {filename_video} -i {filename_audio} -c:v copy -c:a aac -b:a {download_info.audio_bitrate} '{output_file}'",
            shell=True,
        )
        os.remove(filename_audio)
        os.remove(filename_video)

    def download(self, url, referer, output_file):
        logging.info(f"Getting video from {url}")
        response = requests.get(url, headers={"Referer": referer})
        html = response.text
        if html:
            logging.debug(f"Finding player config JSON in {url}")
            player_config_json = self._find_player_config_json(html)

            logging.debug(f"Finding master JSON url in player config JSON")
            master_json_url = self._find_master_json_url(player_config_json)
            download_info = self._get_vimeo_download_info(master_json_url)

            logging.info(f"Downloading video for {url} to {output_file}")
            self._download(output_file, download_info)
        else:
            raise RuntimeError(f"Empty HTML response from {url}")
