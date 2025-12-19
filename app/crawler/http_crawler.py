import requests


class HTTPCrawler:
    def fetch(self, url: str) -> str:
        """
        Fetch raw HTML from a URL.
        
        Args:
            url: The URL to fetch
            
        Returns:
            HTML content as string
            
        Raises:
            Exception on HTTP failure
        """
        response = requests.get(url)
        response.raise_for_status()
        return response.text

