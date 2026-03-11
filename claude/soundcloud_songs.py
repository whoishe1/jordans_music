import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import time


class GetSoundCloud:
    """Scrapes playlists from a SoundCloud user and outputs them as DataFrames.

    Attributes:
        url: url address of soundcloud user sets page,
             e.g. https://soundcloud.com/MyUserAccount/sets
    """

    def __init__(self, url):
        self.url = url
        self.user = url.split("/")[3]

    def _scroll_to_bottom(self, driver, pause=2):
        """Scroll a page until no more content loads."""
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def _get_soup(self, url, scroll_pause=2):
        """Load a URL in Chrome, scroll to bottom, and return parsed BeautifulSoup."""
        driver = webdriver.Chrome()
        try:
            driver.get(url)
            self._scroll_to_bottom(driver, pause=scroll_pause)
            return BeautifulSoup(driver.page_source, "html.parser")
        finally:
            driver.quit()

    def which_playlists(self):
        """Loads all playlists from the user's sets page and returns their URLs."""
        soup = self._get_soup(self.url, scroll_pause=3)

        playlist_links = soup.find_all(
            "a",
            class_="sc-link-primary soundTitle__title sc-link-dark sc-text-h4",
        )

        urls = []
        for link in playlist_links:
            href = link.get("href", "")
            parts = href.split("/")
            if len(parts) >= 3 and parts[1] == self.user and parts[2] == "sets":
                urls.append(f"https://soundcloud.com{href}")

        self.playlist_urls = urls
        return urls

    def get_playlist(self, playlist_url):
        """Retrieve artist and song data from a specific playlist URL.

        Args:
            playlist_url: full URL to a SoundCloud playlist

        Returns:
            pandas DataFrame with trackname, artists, and name_of_playlist columns
        """
        soup = self._get_soup(playlist_url, scroll_pause=1)
        name_of_playlist = playlist_url.split("/")[-1]

        track_names = soup.find_all(
            "a",
            class_="trackItem__trackTitle sc-link-dark sc-link-primary sc-font-light",
        )
        artist_names = soup.find_all(
            "a",
            class_="trackItem__username sc-link-light sc-link-secondary sc-mr-0.5x",
        )

        return pd.DataFrame(
            {
                "trackname": [t.text for t in track_names],
                "artists": [a.text for a in artist_names],
                "name_of_playlist": name_of_playlist,
            }
        )

    # Keep old method name as alias for backwards compatibility with dagster job
    getplaylist = get_playlist

    def __repr__(self):
        return f"GetSoundCloud(url='{self.url}')"
