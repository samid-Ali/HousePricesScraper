# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 17:04:59 2021

@author: Samid
"""

from bs4 import BeautifulSoup
from requests import get
import pandas as pd
import re
import time
import random
import os
from nltk.sentiment import SentimentIntensityAnalyzer

os.chdir("G:/Samid work/Python/House Prices/")
os.getcwd()

headers = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})

sia = SentimentIntensityAnalyzer()
# setting up the lists that will form our dataframe with all the results
titles = []
prices = []
areas = []
zone = []
condition = []
descriptions = []
urls = []
thumbnails = []
bedrooms =[]
Property_Type = []
compundRatings = []
Sentiment= []
Addresses = []


start = time.time()


links = ["https://www.rightmove.co.uk/property-for-sale/find.html?searchType=SALE&locationIdentifier=REGION%5E1217&insId=1&radius=3.0&minPrice=250000&maxPrice=900000&minBedrooms=2&maxBedrooms=5&displayPropertyType=houses&maxDaysSinceAdded=&_includeSSTC=on&sortByPriceDescending=&primaryDisplayPropertyType=&secondaryDisplayPropertyType=&oldDisplayPropertyType=&oldPrimaryDisplayPropertyType=&newHome=&auction=false"]
""" looking at first 3 pages, can see patern page is given by "index =i" 
i.e page 2 is index =24, use following code to calculate a (number of results)
so we can write a while loop to get the page links 
"""

#finding "a"
sapo_url = str(links[0])
r = get(sapo_url, headers=headers)
page_html = BeautifulSoup(r.text, 'html.parser')
HC1 = page_html.find_all('div', class_="searchHeader-title")        #for first page
a= int(re.findall(r'\d+',str(HC1))[0])                              #a = total search results
NumResults = a
    
#getting page links using "a"
i=24
while i <a:
    links.append("https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E1217&maxBedrooms=5&minBedrooms=2&maxPrice=900000&minPrice=250000&radius=3.0&index="+str(i)+"&propertyTypes=detached%2Csemi-detached%2Cterraced&primaryDisplayPropertyType=houses&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords=")
    i+=24
    print(i)   

Links_df = pd.DataFrame(
{'links': links})
#Links_df.to_csv()  

    
# We can now loop our code over these links to scrape our variables
    
start = time.time()  
for url in range(len(links)):
    sapo_url = str(links[0])
    r = get(sapo_url, headers=headers)
    page_html = BeautifulSoup(r.text, 'html.parser')
    house_containers = page_html.find_all('div', class_="l-searchResult is-list")
    if house_containers != []:
        for idx, container in enumerate(house_containers):
                
            
            #Price  
            p = re.findall(r"propertyCard-priceValue(.*?) </div", str(house_containers[idx]))
            price = str(re.findall(r'£\d*,\d*', str(p))).strip("['£']").replace(",","")
            # str(re.findall(r'£\d*,\d*', str(house_containers[idx]))).strip("['£']").replace(",","")
            prices.append(int(price))
            

            # Description
            d = re.findall(r'(?<=property-description" itemprop="description">).*', str(house_containers[idx]))      # everything excluding x using  (?<=x).*
            descriptions.append(d[0])
            
            #Sentiment
            desc = pd.Series( (desc[0] for desc in descriptions) )      # convert to series for nltk
            Sentiment.append(sia.polarity_scores(desc[idx]))
            
            #Compound 
            compoundRating = sia.polarity_scores(desc[idx])["compound"]
            compundRatings.append(compoundRating)
            
            # Title
            t = re.findall(r'(?<=itemprop="name">\n).*', str(house_containers[idx]))
            titles.append(t)
            
            # Bedrooms
            b = re.search(r'\d', str(t)).group()
            bedrooms.append(b)
            
            # Property type
            pt = re.findall(r'(?<=\d bedroom) .* for sale', str(t))
            Property_Type.append(str(pt).strip("['']").replace("for sale",""))
            
            #URLs
            u = re.findall(r'(?<=propertyCard-link" href=).*', str(house_containers[idx]))
            URL ="https://www.rightmove.co.uk" + str(u).strip("['']>").strip('"')
            urls.append(URL)
            
            #Adress
            ad = re.findall(r'(?<=itemprop="addressCountry"/>\n<span>).*(?<=<)', str(house_containers[idx]))
            Addresses.append(ad[0].strip("<"))
            
    else:
        break
    
    time.sleep(random.randint(1,3))
       
    Houses_df = pd.DataFrame(
    {'Prices': prices,
     'Number of Bedrooms': bedrooms,
     'Property type': Property_Type,
     'Sentiment List': Sentiment,
     'Compound Sentiment': compundRatings,
     'Link': urls,
     'Title': titles,
     'Description': descriptions,
     'Addresses': Addresses
    })


end = time.time() - start


file = "House_prices_" + str(round(end)) +".tsv"

Houses_df.to_csv(file, sep="\t")  
print(end)          
