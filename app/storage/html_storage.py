import os


class HTMLStorage:
    def __init__(self, base_path: str = "data/html"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)
    
    def save(self, crawl_id: str, html: str) -> str:
        """
        Save HTML content to disk.
        """
        file_path = os.path.join(self.base_path, f"{crawl_id}.html")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return file_path

