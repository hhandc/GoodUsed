import requests
from bs4 import BeautifulSoup

webpage = requests.get ("https://www.daangn.com/hot_articles")
soup = BeautifulSoup (webpage.content,"html.parser")

# print (soup)
# print(soup .div)
# for child in soup. hi.children:
# print(child)
getItem = soup.select("#content › section.cards-wrap › article")
print(getItem[0])

##content > section.cards-wrap > article:nth-child(1) > a > div.card-desc > h2 for item in getItem:

for item in getItem:
    print (item.select('a > div.card-desc > h2 ')[0].text.strip(), end = ",")
    print (item.select('a > div.card-desc > div.card-price')[0].text.strip(), end = ",")
    print (item.select('a > div.card-desc > div.card-region-name')[0].text.strip(), end = ",")
    print (item.select('a > div.card-desc > div.card-counts')[0].text.strip().replace(' ', '').replace('\n', '').replace('.', ','))
        
# #content > section.cards-wrap > article:nth-child(1) > a > div.card-desc ›div.card-region-name
# count = 0
# for img in soup. find all(attrs= 'class'; 'card-desc'1):
# # print (count, img-get_text ())
# count = count +1
# 정규식을 사용할 수도 있음
# copy selector
# print (getImage)
# content > section.cards-wrap › article:nth-child(72) › a › div.card-photo › img# getimage = soup. select ("#hot-articles-head-title")