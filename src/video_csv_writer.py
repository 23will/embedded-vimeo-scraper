import csv
import logging
from dataclasses import dataclass


@dataclass
class VideoCsvWriter:
    csv_path: str

    def write_videos_to_csv(self, videos):
        logging.info(f"Writing {len(videos)} video rows to CSV")
        with open(self.csv_path, "w") as stream:
            csv_writer = csv.writer(stream)
            csv_writer.writerow(
                ["section", "name", "embedded_url", "parent_url", "url", "title"]
            )
            for (section, name), video in videos.items():
                csv_writer.writerow(
                    [
                        section,
                        name,
                        video.embedded_url,
                        video.parent_url,
                        video.url,
                        video.title,
                    ]
                )
