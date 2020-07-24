from bs4 import BeautifulSoup
from pandas import read_csv
from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from time import sleep
import tweepy
import urllib.request
import urllib.parse


def get_api_auth():
    """
    Function to authenticate with the Twitter Api
    :returns: authentication environment
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
    except Exception as e:
        print(e)
        print("Authentication failed!")


def download_image(url, it, path):
    """
    With provided parameters this function downloads image files from Wikiart.org
    :param url: url to Wikiart.org image
    :param it: integer value
    :param path: path to project folder
    :returns: image location path
    """
    try:
        print("Retrieving image " + str(it) + " from: " + url)
        session = Session()
        retry = Retry(connect=3, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        response = session.get(url)
        soup = BeautifulSoup(response.text, "html.parser", from_encoding="utf-8")
        tag = soup.findAll('img')[0]
        link = tag['src']
        print("Image: " + link)
        # If image dummy then return None
        if link == "https://uploads.wikiart.org/Content/images/FRAME-600x480.jpg":
            print("Dummy Image")
            image_path = None
        else:
            image_path = path + '/images/img_' + str(it) + '.jpg'
            url = urllib.parse.urlparse(link)
            url = url.scheme + "://" + url.netloc + urllib.parse.quote(url.path)
            urllib.request.urlretrieve(url, image_path)
        return image_path
    except Exception as e:
        print(e)
        print("Image retrieval number " + str(it) + " failed!")


def send_tweet(message, media, it, api):
    """
    This function sends out a tweet with the downloaded image (download_image())
    :param message: a tweet
    :param media: the image location path
    :param it: integer value
    :param api: authentication environment (get_api_auth())
    :returns: none (void function)
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
    :param path: path to project folder
    :returns: none (void function)
    """
    api_auth = get_api_auth()
    print("Reading data file...")
    df = read_csv(path + '/artset.csv', sep=',', header=None)
    df_sample = df.sample(4)
    i = 1
    for num, tweet, source in df_sample.values:
        media_location = download_image(source, i, path)
        if media_location is not None:
            send_tweet(tweet, media_location, i, api_auth)
        sleep(2)
        i += 1
    print("Done.")


if __name__ == "__main__":
    project_path = '...'
    main(project_path)
