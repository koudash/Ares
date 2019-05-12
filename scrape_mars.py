# Dependencies
from splinter import Browser
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import datetime as dt
import time

def init_browser():
    # Use Chrome to scrape the following urls
    executable_path = {'executable_path': './chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)

def scrape():
    '''
    Scrape Mars data (latest news, featured image, weather, fact and hemisphere) from five different
    websites and return the results in dictionary format 
    '''
    
    # Dict to store scraped Mars data
    mars_fact = {}

    # Use Chrome for scraping
    browser = init_browser()

    # >>> SCRAPING 1 >>> Mars Latest News >>> START >>> 
    # 
    #
     
    # Url for NASA Mars News Site
    news_url= 'https://mars.nasa.gov/news'
    
    # Navigate to url
    browser.visit(news_url)
    
    # Parse HTML with BeautifulSoup
    soup = bs(browser.html, 'html.parser')

    # Setup explicit wait time for javascript to load the webpage
    time.sleep(1)

    # Find the first tag in which news title and paragraph locate
    news_tag = soup.find('li', class_='slide').find('div', class_='list_text')

    # Retrieve the title and paragraph for the latest news
    news_title = news_tag.find('div', class_='content_title').text
    news_p = news_tag.find('div', class_='article_teaser_body').text
    news_date = news_tag.find('div', class_='list_date').text

    # Save the latest news in a dict
    mars_news = {
        'NASA_News_Title': news_title,
        'NASA_News_Para': news_p,
        'NASA_News_date': news_date
    }

    # Save title and paragraph for the latest Mars news to "mars_fact"
    mars_fact["Mars_News"] = mars_news
    
    # 
    # 
    # <<< END <<< Mars Latest News <<< SCRAPTING 1 <<<

    # >>> SCRAPING 2 >>> Mars Featured Image >>> START >>> 
    # 
    #
     
    # Url for Mars Space Image from Jet Propulsion Laboratory
    image_url= 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'

    # Navigate to url
    browser.visit(image_url)

    # Parse HTML with BeautifulSoup
    soup = bs(browser.html, 'html.parser')

    # Retrieve relative path for featured image
    rel_path = soup.find('article', class_='carousel_item')['style']

    # Since "/" is not in string "?search=&category=Mars", right strip() "image_url" for concatenation 
    featured_img_url = image_url.rstrip("?search=&category=Mars") + rel_path[36:-3]

    # Save Mars featured image to "mars_fact"
    mars_fact['Featured_Image_url'] = featured_img_url
    
    # 
    # 
    # <<< END <<< Mars Featured Image <<< SCRAPTING 2 <<<

    # >>> SCRAPING 3 >>> Mars Weather >>> START >>> 
    # 
    #
     
    # Url for Mars Weather on Twitter
    news_url= 'https://twitter.com/marswxreport?lang=en'

    # Navigate to url
    browser.visit(news_url)

    # Parse HTML with BeautifulSoup
    soup = bs(browser.html, 'html.parser')

    # Find tags that contain Mars temperature
    # Note that not all 'div' tags with the class of "content" is about Mars temperature tweet
    content_tags = soup.find_all('div', class_='content')

    # Loop through "content" tags
    for content in content_tags:
        
        try:
            # Assign child 'div' tag with the class of "stream-item-header" to "header" 
            header = content.find('div', class_='stream-item-header')
            
            # Look for full name and username in stream header      
            full_name = header.a.find('span', class_='FullNameGroup').text[1:].rstrip('\u200f\xa0')
            username = header.a.find('span', class_='username').text

            # Mars temperature is tweeted by "MarsWxReport" as "Mars Weather"
            if full_name == 'Mars Weather' and username == '@MarsWxReport':
                
                # Retrieve content of the tweet for Mars temperature
                # Note that if 'div' (class="stream-item-header") exists, so does that with class of
                # "js-tweet-text-container"
                mars_weather = content.find('div', class_='js-tweet-text-container').p.text[:-26]
                
                # Jump out of iteration once the latest Mars temperature is found
                break        
            
        # Set exception for "content" tag without child 'div' (class="stream-item-header")   
        except:
            pass

    # Save Mars weather to "mars_fact"
    mars_fact['Weather_Brief'] = mars_weather

    # 
    # 
    # <<< END <<< Mars Weather <<< SCRAPTING 3 <<<

    # >>> SCRAPING 4 >>> Mars Fact >>> START >>> 
    # 
    #     

    # Url for Mars facts on Space Fact website
    fact_url= 'https://space-facts.com/mars/'

    # Navigate to url
    browser.visit(fact_url)

    # Parse HTML with BeautifulSoup
    soup = bs(browser.html, 'html.parser')

    # List to store data from "Mars Planet Profile" table
    cols = []

    # Anchor contents of "Mars Planet Profile" table
    table = soup.find('table', class_='tablepress')

    # Retrieve all rows from the table
    rows = table.tbody.find_all('tr')

    # Loop through each row to scrape column data of interest and append to "cols" list
    for row in rows:
        col_queries = row.find_all('td')
        col = [col_queries[i].text.strip() for i in range(2)]
        cols.append(col)

    # Setup a Pandas DataFrame to store column data from "cols"
    mars_fact_df = pd.DataFrame(columns=['Parameters', 'Values'])

    mars_fact_df['Parameters'] = [cols[i][0] for i in range(len(cols))]
    mars_fact_df['Values'] = [cols[i][1] for i in range(len(cols))]

    # Save Mars fact data as html table
    # Setting the text in "text-info" color to show hover effect
    fact_html = mars_fact_df.to_html(header=True, index=False)

    # 1. Remove "style" info. for tr in thead and then add class ("text-center") to 'tr' in thead
    im1 = fact_html.split(' style="text-align: right;"')
    im1_html = im1[0] + " class='text-center'" + im1[1]

    # 2. Add class info at "<th>"
    im2 = im1_html.split('<th>')
    for i in range(1, len(im2)):
        im2[i] = "<th class='table-bg-change font-italic'>" + im2[i]

    # 3. Concatenate the new html
    im2_html = ''
    for i in range(len(im2)):
        im2_html += im2[i]

    # 4. Add class info at "<td>"
    im3 = im2_html.split('<td>')
    for i in range(1, len(im3)):
        im3[i] = "<td class='table-bg-change'>" + im3[i]

    # 5. Concatenate the new html
    fact_html2 = ''
    for i in range(len(im3)):
        fact_html2 += im3[i]

    # Save Mars fact table data to "mars_fact"
    mars_fact['Fact_Table'] = fact_html2

    # 
    # 
    # <<< END <<< Mars Fact <<< SCRAPTING 4 <<<

    # >>> SCRAPING 5 >>> Mars Hemispheres >>> START >>> 
    # 
    #     

    # Url for Mars facts on USGS Astrogeology
    hemisph_url= 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    # Navigate to url
    browser.visit(hemisph_url)

    # Parse HTML with BeautifulSoup
    soup = bs(browser.html, 'html.parser')

    # List to store dict that containing hemisphere title and image url string  
    hemisph_img_urls = []

    # Find tags that contain 'div' with the class of "item"
    item_tags = soup.find_all('div', class_='item')

    # Loop through "item" tags
    for item in item_tags:
        
        # Retrieve hemisphere title
        title = item.h3.text
        
        # Concatenate child_url
        child_url = hemisph_url[:29] + item.find('a', class_='itemLink')['href']
        
        # Navigate to the child url
        browser.visit(child_url)
        
        # Parse child url with BeautifulSoup
        soup = bs(browser.html, 'html.parser')
        
        # Setup explicit wait time for javascript to load the webpage
        time.sleep(2)
        
        # Concatenate the url for high resolution image
        hi_r_img = hemisph_url[:29] + soup.find('img', class_='wide-image')['src']
        
        # Append hemisphere title and image url string to "hemisph_img_urls" as dict
        hemisph_img_urls.append({'title': title, 'img_url': hi_r_img})

    # Save Mars hemisphere title and image url data to "mars_fact"
    mars_fact['Hemispheres'] = hemisph_img_urls

    # 
    # 
    # <<< END <<< Mars Hemispheres <<< SCRAPTING 5 <<<

    # Take a note on scraping local date and time and save in "mars_fact"
    mars_fact['Data_Retrv_D&T'] = dt.datetime.now()

    # Close all browsers if still active
    browser.quit()

    # Return results
    return mars_fact