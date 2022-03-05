import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import time


# WEBDRIVER_PATH = "C:/Users/Jordan/Documents/webdriver/chromedriver.exe"


class GetSoundCloud:
    """Scrapts playlists from a Soundcloud user and outputs them into excel format

    Attributes:
        url: url address of soundcloud user.  i.e. https://wwww.soundcloud.com/MyUserAccount/sets
    """

    def __init__(self, url):
        """Initialize GetSoundCloud Object"""
        self.url = url

    def which_playlists(self):
        """Loads all playslist from url page and saves the playlist names (slug) into a list"""

        this_url = self.url
        user = self.url.split("/")[3]
        driver = webdriver.Chrome()
        try:
            driver.get(this_url)
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            soup = BeautifulSoup(driver.page_source, "html.parser")

            playlist_extensions = soup.find_all(
                "a",
                class_={"sc-link-primary soundTitle__title sc-link-dark sc-text-h4"},
            )

            extensions_list = [str(ext.get("href")) for ext in playlist_extensions]

            corr_ext = []
            for i in extensions_list:
                splt = i.split("/")
                if splt[1] == user and splt[2] == "sets":
                    corr_ext.append(i)

            these_urls = [("https://soundcloud.com" + i) for i in corr_ext]
            self.playlist_urls = these_urls
        finally:
            driver.quit()
            return these_urls

    # Returns playlist in dataframe format
    def getplaylist(self, this_url):
        """
        Retrieve artist and song from specified playlist

        Args:
            this_url: specific playlist url from the which_playlists method

        Returns:
            DataFrame: pandas dataframe of Artists and Tracknames of playlist

        """
        driver = webdriver.Chrome()
        try:
            driver.get(this_url)
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            soup = BeautifulSoup(driver.page_source, "html.parser")

            track_names = soup.find_all(
                "a",
                class_={
                    "trackItem__trackTitle sc-link-dark sc-link-primary sc-font-light"
                },
            )
            artist_names = soup.find_all(
                "a", class_={"trackItem__username sc-link-light sc-link-secondary"}
            )

            tracknames_list = [str(names.text) for names in track_names]

            artistnames_list = [str(names.text) for names in artist_names]

            playlist = pd.DataFrame(
                {
                    "trackname": pd.Series(tracknames_list),
                    "artists": pd.Series(artistnames_list),
                }
            )

        finally:
            driver.quit()
            return playlist

    def __repr__(self):
        return f"The set url is {self.url}"
