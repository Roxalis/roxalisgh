from bs4 import BeautifulSoup
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time
import tweepy
import urllib.request


def get_api_auth():
    """
    Function to authenticate with the Twitter Api

    Returns authentication environment
    """
    try:
        print("Authenticating with Twitter...")
        consumer_key = '...'
        consumer_secret = '...'
        access_token = '...'
        access_secret = '...'

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)

        return tweepy.API(auth)

    except:
        print("Authentication failed!")


def download_image(url, it, path):
    """
    With provided parameters this function downloads image files from Wikiart.org

	url: url to Wikiart.org image
	it: integer value
	path: path to project folder

    Returns image location path
	"""
    try:
        print("Retrieving image " + str(it) + " ...")
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        response = session.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        tag = soup.findAll('img')[0]
        link = tag['src']
        print("Image: " + link)
        urllib.request.urlretrieve(link, path + '/images/img_' + str(it) + '.jpg')
        return path + '/images/img_' + str(it) + '.jpg'
    except Exception as e:
        print(e)
        print("Image retrieval number " + str(it) + " failed!")


def send_tweet(message, media, it, api):
    """
    This function sends out a tweet with the downloaded image (download_image())

	message: a tweet
	media: the image location path
	it: integer value
	api: authentication environment (get_api_auth())

	Returns none (void function)
	"""
    try:
        print("Sending tweet " + str(it) + " ...")
        media_list = []
        response = api.media_upload(media)
        media_list.append(response.media_id_string)
        api.update_status(message, media_ids=media_list)
    except Exception as e:
        print(e)
        print("Sending tweet " + str(it) + " failed!")


def main(path):
    """
    Main function to authenticate with Twitter, load the artwork data file, chooses 4 artworks
	randomly, downloads required images, and tweets the artwork with artwork information.

	path: path to project folder

	Returns none (void function)
	"""
    api_auth = get_api_auth()
    print("Reading data file...")
    df = pd.read_csv(path + '...', sep=',', header=None)
    df_sample = df.sample(4)
    i = 1
    for num, tweet, source in df_sample.values:
        media_location = download_image(source, i, path)
        send_tweet(tweet, media_location, i, api_auth)
        time.sleep(2)
        i += 1
    print("Done.")


if __name__ == "__main__":
    project_path = '...'
    main(project_path)
