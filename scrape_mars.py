from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import requests
import time

def init_browser():
    #Getting Chrome Driver and browser
    executable_path = {"executable_path":"chromedriver.exe"}
    return Browser("chrome", **executable_path, headless = False)

def scrape():
    mars_facts_dict = {}
    browser = init_browser()
    mars_facts_dict = dict(zip(['latest_news_title','latest_news_paragraph'], get_latest_news(browser)))
    
    mars_facts_dict['featured_image_url'] = get_jpl_image_url(browser)
    mars_facts_dict['mars_weather'] = get_mars_weather_tweet(browser) 
    mars_facts_dict['mars_facts_html_table'] = get_mars_facts(browser)
    mars_facts_dict['hemi_info'] = get_mars_hemispheres_title_url(browser) 
    return mars_facts_dict

def get_latest_news(browser):
    # URL of page to be scraped
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    time.sleep(5)
    #using BeautifulSoup to write it into html
    html = browser.html
    soup = BeautifulSoup(html,"html.parser")

    # Getting the most recent news title and paragraph
    return  soup.find("div",class_="content_title").text, soup.find("div", class_="article_teaser_body").text


def get_jpl_image_url(browser):
    # Go to the JPL website
    url_image = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url_image)
    time.sleep(5)
    #Use BeautifulSoup to write it into html
    html_image = browser.html
    image_soup = BeautifulSoup(html_image,"html.parser")#lxml
    
    # Find image url for current featured mars image
    featured_image = (image_soup.find('div', class_='default floating_text_area ms-layer')).find('footer')
    return 'https://www.jpl.nasa.gov'+ featured_image.find('a')['data-fancybox-href']


def get_mars_weather_tweet(browser):

    # Go to the Mars Weather website
    url_mars_weather = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url_mars_weather)

    html_mars_weather = browser.html
    mars_weather_soup = BeautifulSoup(html_mars_weather,"html.parser")#lxml

    #Get most recent tweet.
    return mars_weather_soup.find("p", class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text").text
    
def get_mars_facts(browser):
    #Mars Facts

    url_facts = "http://space-facts.com/mars/"
    mars_facts_df = pd.read_html(url_facts)[0]
    mars_facts_df.columns=['Attribute','Value']
    mars_facts_df.set_index(['Attribute'], inplace=True)

    mars_facts_html_table = mars_facts_df.to_html()
    return mars_facts_html_table.replace("\n", "")
   
def get_mars_hemispheres_title_url(browser):
    #Mars Hemisphere

    # Go to the Mars Hemisphere website
    url_mars_hemi = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url_mars_hemi)

    mars_hemi_html = browser.html
    mars_hemi_soup = BeautifulSoup(mars_hemi_html, "html.parser")#lxml

    #Get image items on page. These coordinate with the 4 hemispheres
    base_url ="https://astrogeology.usgs.gov"

    images_array = mars_hemi_soup.find_all('div', class_='item')

    # Create list to store dictionaries of data
    hemi_image_urls = []

    # Loop through each hemisphere and click on link to find large resolution image url
    for image in images_array:
        href = image.find('a', class_='itemLink product-item')
        link = base_url + href['href']
        browser.visit(link)

        time.sleep(5)

        hemi_html2 = browser.html
        hemi_soup2 = BeautifulSoup(hemi_html2, "html.parser")

        hemi_title = hemi_soup2.find('div', class_='content').find('h2', class_='title').text
        if hemi_title.endswith('Enhanced'):
            hemi_title = hemi_title[:-9]
    
        hemisphere_info = {'title': hemi_title, 'img_url': hemi_soup2.find('div', class_='downloads').find('a')['href']}
        print(hemisphere_info)
        # Append dictionary to list
        hemi_image_urls.append(hemisphere_info)

    return hemi_image_urls