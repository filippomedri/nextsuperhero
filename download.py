from bs4 import BeautifulSoup
import requests

import os
from urllib.request import urlretrieve

def download_files(directory = 'mta_data',how_many=None):
    # Retrieve the link list from the web page
    link_list = []

    r  = requests.get("http://web.mta.info/developers/turnstile.html")
    data = r.text
    soup = BeautifulSoup(data,'html5lib')
    for link in soup.findAll('a'):
        link_list.append(link.get('href'))

    # Filter the file list from the link list
    file_list = []
    for link in link_list :
        if link is not None:
            if 'data/nyct/turnstile/turnstile' in link:
                            file_list.append(link)

    # How many file to download
    if (how_many == None):
            short_file_list = file_list
    else :
        short_file_list = file_list[:how_many]

    if not os.path.exists(directory):
        os.makedirs(directory)

    # Download files in 'directory'
    prefix = "http://web.mta.info/developers/"
    for filename in short_file_list:
        short_file_name = filename.replace('data/nyct/turnstile/','')
        fullfilename = os.path.join(directory, short_file_name)
        if not os.path.exists(fullfilename):  # if you already download it, it will skip
            url = prefix + filename
            print (url,fullfilename)
            urlretrieve(url, fullfilename)