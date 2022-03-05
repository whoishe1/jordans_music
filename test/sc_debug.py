import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import time


def which_playlists():
    """Loads all playslist from url page and saves the playlist names (slug) into a list"""

    url = "https://soundcloud.com/whoishe1/sets"

    this_url = url
    user = url.split("/")[3]
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

        # Usually there is an frontend change in soundcloud, so you need to check if the CSS has changed.
        playlist_extensions = soup.find_all(
            "a", class_={"sc-link-primary soundTitle__title sc-link-dark sc-text-h4"}
        )

        extensions_list = [str(ext.get("href")) for ext in playlist_extensions]

        corr_ext = []
        for i in extensions_list:
            splt = i.split("/")
            if splt[1] == user and splt[2] == "sets":
                corr_ext.append(i)

        these_urls = [("https://soundcloud.com" + i) for i in corr_ext]
        playlist_urls = these_urls
    finally:
        driver.quit()
        return these_urls


def getplaylist():
    """
    Retrieve artist and song from specified playlist

    Args:
        this_url: specific playlist url from the which_playlists method

    Returns:
        DataFrame: pandas dataframe of Artists and Tracknames of playlist

    """

    this_url = "https://soundcloud.com/whoishe1/sets/8_a"

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

        # Usually there is an frontend change in soundcloud, so you need to check if the CSS has changed.
        track_names = soup.find_all(
            "a",
            class_={"trackItem__trackTitle sc-link-dark sc-link-primary sc-font-light"},
        )
        artist_names = soup.find_all(
            "a", class_={"trackItem__username sc-link-light sc-link-secondary"}
        )

        tracknames_list = [str(names.text) for names in track_names]

        artistnames_list = [str(names.text) for names in artist_names]

        playlist = pd.DataFrame(
            {
                "Tracks": pd.Series(tracknames_list),
                "Artists": pd.Series(artistnames_list),
            }
        )

    finally:
        driver.quit()
        return playlist
