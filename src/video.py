from dataclasses import dataclass


@dataclass
class Video:
    title: str
    url: str
    embedded_url: str
    parent_url: str