import requests


class HTTPCrawler:
    def fetch(self, url: str) -> str:
        """
        Fetch raw HTML from a URL.
        """
        response = requests.get(url)
        response.raise_for_status()
        return response.text

