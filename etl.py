import os
import re
import time
import numpy as np
import pandas as pd
import pickle

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

store_directory = 'resources'
data_directory = 'data'
links_list_store = 'links_'
movies_df_store = 'movies_'
tv_series_df_store = 'tv_series_'


def create_movie_df():
    df = pd.DataFrame(columns=['Title',
                               'Duration(Min)',
                               'ReleaseDate',
                               'Score',
                               'NoUsersRating',
                               'MetaScore',
                               'NoReviews-Users',
                               'NoReviews-Crit',
                               'OpeningWE(USA)($)',
                               'Gross(USA)($)',
                               'CumulativeWorldWide Gross($)'
                               ])
    return df

def insert_movie_info(from_page, to_data_frame, at_row):

    at_row+=1
    try:

        # Anagrafic Data
        html_tag = from_page.find('meta', property='og:title')
        if html_tag != None:
            to_data_frame.loc[at_row, 'Title'] = html_tag['content']
        html_tag = from_page.find('time',itemprop='duration')
        if html_tag != None:
            to_data_frame.loc[at_row, 'Duration(Min)'] =int(re.search(r'PT(\d+)M',html_tag['datetime']).group(1))
        html_tag = from_page.find('meta', itemprop='datePublished')
        if html_tag != None:
            to_data_frame.loc[at_row, 'ReleaseDate'] = pd.to_datetime(html_tag['content']).date()

        # Score & Review Data
        html_tag = from_page.find('span', itemprop='ratingValue')
        if html_tag != None :
            to_data_frame.loc[at_row,'Score'] = float(html_tag.text)/10.0
        html_tag = from_page.find('span', itemprop='ratingCount')
        if html_tag != None :
            to_data_frame.loc[at_row,'NoUsersRating'] = int((re.sub(',', '', html_tag.text)))
        html_tag = from_page.find('div', {"class" : "metacriticScore score_favorable titleReviewBarSubItem"})
        if html_tag != None:
            to_data_frame.loc[at_row,'MetaScore'] = float(re.sub(r'\n','',html_tag.text))
        html_tag =  from_page.find('a', href="reviews?ref_=tt_ov_rt")
        if html_tag != None:
            to_data_frame.loc[at_row,'NoReviews-Users'] = int(
                                                            re.sub(',','',
                                                            re.search(r'(\d{1,3}(,\d{3})*)',html_tag.text)
                                                                   .group(1)
                                                                   )
                                                            )
        html_tag = from_page.find('a', href="externalreviews?ref_=tt_ov_rt")
        if html_tag != None:
            to_data_frame.loc[at_row, 'NoReviews-Crit'] = int(
                                                            re.sub(',','',
                                                            re.search(r'(\d{1,3}(,\d{3})*)', html_tag.text)
                                                                   .group(1)
                                                                   )
            )

        # Box Office Data

        html_tag = from_page.find('h4', string = 'Opening Weekend USA:')
        if html_tag != None:
            html_tag = html_tag.parent.text.split()[3]
            html_tag = re.sub(r'\$|,', '', html_tag)
            if html_tag != None:
                to_data_frame.loc[at_row, 'OpeningWE(USA)($)'] = int(html_tag)

        html_tag = from_page.find('h4', string='Gross USA:')
        if html_tag != None:
            html_tag = html_tag.parent.text.split()[2]
            html_tag = re.sub(r'\$|,', '', html_tag)
            if html_tag != None:
                to_data_frame.loc[at_row, 'Gross(USA)($)'] = int(html_tag)

        html_tag = from_page.find('h4', string='Cumulative Worldwide Gross:')
        if html_tag != None:
            html_tag = html_tag.parent.text.split()[3]
            html_tag = re.sub(r'\$|,', '', html_tag)
            if html_tag != None:

                    to_data_frame.loc[at_row, 'CumulativeWorldWide Gross($)'] = int(html_tag)
    except Exception:
        print(str(Exception))

    return (to_data_frame, at_row)

def create_tv_series_df():
    df = pd.DataFrame(columns=['Title',
                               'Season',
                               'Year'
                               ])
    return df

def insert_series_info(from_page, to_data_frame,at_row):

    try:
        # Anagrafic Data
        html_tag = from_page.find('meta', property='og:title')
        title = html_tag['content']

        # Seasons
        html_tag = from_page.find('div', {'class' : 'seasons-and-year-nav'})
        count_child = 0
        child_list = []
        if (html_tag != None):
            for child in html_tag.descendants:
                if '/title/tt' in str(child):
                    count_child += 1
                    child_list.append(child.text)
            # First half of link are season number, of the other half the first is a span, so we took the rest
            child_list = child_list[(count_child//2)+1:]
            child_list.reverse()
        else :
            html_tag = from_page.find('meta', itemprop='datePublished')
            if html_tag != None:
                at_row += 1
                child_list = [pd.to_datetime(html_tag['content']).year]

        for season, year in enumerate(child_list):
            at_row += 1
            to_data_frame.loc[at_row, 'Title'] = title
            to_data_frame.loc[at_row, 'Season'] = season+1
            to_data_frame.loc[at_row, 'Year'] = year
    except Exception:
        print(str(Exception))

    return (to_data_frame,at_row)

def update(links_list,with_page_to_parse):

    temp_list = []
    data = with_page_to_parse.get_attribute('innerHTML')
    soup = BeautifulSoup(data, 'html5lib')
    for link in soup.findAll('a'):
        temp_list.append(link.get('href'))

    # Filter the movie links list from the link list
    for link in temp_list:
        if link is not None:
            if '/title/tt' in link:
                if '_li_tt' in link:
                    links_list.append('https://www.imdb.com' + link)
    return links_list


chrome_driver = "./chromedriver"
os.environ["webdriver.chrome.driver"] = chrome_driver
driver = webdriver.Chrome(chrome_driver)

super_hero_url_desc = "https://www.imdb.com/search/title?keywords=superhero&explore=title_type,genres&pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=15aedf0d-e467-4a1a-922a-e0cbd7299e84&pf_rd_r=49MWE1P2RCWXVANP5V7Z&pf_rd_s=center-5&pf_rd_t=15051&pf_rd_i=genre&view=simple&sort=release_date,asc&ref_=ft_gnr_pr5_i_3"
super_hero_url = "https://www.imdb.com/search/title?keywords=superhero&explore=title_type,genres&pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=15aedf0d-e467-4a1a-922a-e0cbd7299e84&pf_rd_r=49MWE1P2RCWXVANP5V7Z&pf_rd_s=center-5&pf_rd_t=15051&pf_rd_i=genre&view=simple&sort=release_date,desc&ref_=ft_gnr_pr5_i_3"

try:
    if (False) :
        driver.get(super_hero_url)
        title_range_description = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'desc'))
        )

        # Search for the number of pages of links to download
        match = r'(\d{1,3}(,\d{3})*) to (\d{1,3}(,\d{3})*) of (\d{1,3}(,\d{3})*)'
        search = re.search(match, title_range_description.text)
        how_many_links_in_page = search.group(3)
        how_many_titles = search.group(5)
        how_many_links_in_page = int(re.sub(',', '', how_many_links_in_page))
        how_many_titles = int(re.sub(',', '', how_many_titles))
        how_many_pages_to_load = how_many_titles // how_many_links_in_page

        # substitute print with log
        print(how_many_links_in_page, how_many_titles, how_many_pages_to_load)

        # Extract the links and save them
        with_content = driver.find_element_by_id('content-2-wide')
        links_list = []
        links_list = update(links_list,with_content)

        links_list_store_count = 1
        links_list_store_file = links_list_store + str(links_list_store_count) +'.pickle'
        with open(os.path.join(store_directory,links_list_store_file), 'wb') as f:
                pickle.dump(links_list, f)
        f.close()


        for i in range(2,how_many_pages_to_load+1):
        #if False:
            seed = np.random.poisson(17)
            print('seed = ',seed)
            WebDriverWait(driver, np.random.poisson(seed))
            next = driver.find_element_by_partial_link_text('Next')
            next.click()
            with_content = driver.find_element_by_id('content-2-wide')
            update(links_list, with_content)
            links_list_store_count += 1
            links_list_store_file = links_list_store + str(links_list_store_count) +'.pickle'
            with open(os.path.join(store_directory,links_list_store_file), 'wb') as f:
                pickle.dump(links_list, f)
            f.close()
    else:
        f = 'links.pickle'
        links_list = pickle.load(open(f,'rb'))


        movies_df = create_movie_df()
        tv_series_df = create_tv_series_df()
        at_mv_row = at_tv_row = 0
        movies_df_store_count = 0
        tv_series_df_store_count = 0
        try:
            for link in links_list:
                seed = np.random.poisson(11)
                print('seed = ', seed)
                WebDriverWait(driver, np.random.poisson(seed))
                #link = 'https://www.imdb.com/title/tt0305075/?ref_=adv_li_tt'
                data = driver.get(link)
                from_soup = BeautifulSoup(driver.page_source, 'html5lib')
                content_type = from_soup.find('meta', property ='og:type')
                if content_type['content']=='video.movie':
                    movies_df, at_mv_row = insert_movie_info(from_soup,movies_df,at_mv_row)
                    movies_df_store_count+=1
                    if (movies_df_store_count%50 == 0):
                        movies_df_store_file = movies_df_store + str(movies_df_store_count)
                        movies_df.to_csv(os.path.join(store_directory,movies_df_store_file))
                if content_type['content']=='video.tv_show':
                    tv_series_df,at_tv_row= insert_series_info(from_soup,tv_series_df,at_tv_row)
                    tv_series_df_store_count += 1
                    if (tv_series_df_store_count%50 != 0):
                        tv_series_df_store_file = tv_series_df_store + str(tv_series_df_store_count)
                        tv_series_df.to_csv(os.path.join(store_directory,tv_series_df_store_file))

            movies_df_store_file = movies_df_store + 'final'
            movies_df.to_csv(os.path.join(data_directory, movies_df_store_file))
            tv_series_df_store_file = tv_series_df_store + 'final'
            tv_series_df.to_csv(os.path.join(data_directory, tv_series_df_store_file))
        except Exception:
            pass
finally:
    print("Broken link ", link)
    driver.quit()