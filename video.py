from dataclasses import dataclass


@dataclass
class Video:
    title: str
    url: str
    embedded_url: str
    parent_title: str
    parent_url: str


    def get_filename(self):
        return self.parent_title if self.title in self.parent_title else f'{self.parent_title}_{self.title}'


    def get_filename_long(self, root_url):
        sanitized_url = self.parent_url.replace(root_url, '').lstrip('/').replace('/#respond','').replace('/', '_')
        return f'{sanitized_url}_{self.get_filename()}'


    def __iter__(self):
        return iter([self.title, self.url, self.embedded_url, self.parent_title, self.parent_url])

