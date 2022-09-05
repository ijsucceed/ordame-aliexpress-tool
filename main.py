import time

import aliexpress
import helper as fn
import sys

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

print()
print('Welcome to AliExpress Product Rating System')
print()
link = input('Enter product link: ') # base url

if fn.isLinkValid(link) is False:
    print('Error: Please enter a valid aliexpress product page link e.g https://www.aliexpress.com/item/2251832665683450.html')
    sys.exit()

print()
print('extracting data from link...this may take few minutes.')
print()

# access the chrome driver
# in incognito mode
# without opening the browser dialog
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920x1080")
options.add_argument("start-maximised")

driver = webdriver.Chrome(options=options)
driver.get(link) # make request

try:
    # scroll down to the bottom of the page
    driver.execute_script("window.scrollTo(0,document.body.clientHeight)") 
    time.sleep(1)

    page_source = driver.page_source

    # initialize beautiful soup
    soup = BeautifulSoup(page_source, "html.parser")
    root_element = soup.find(id="root")
    header_element = soup.find(id="header")

    if root_element == None or header_element == None:
        print('Product or store not found. Make sure you enter a valid link e.g https://www.aliexpress.com/item/2251832665683450.html')
        sys.exit()

    # get store element
    store_status_element = header_element.find('span', class_='top-rated-seller')
    store_followers_element = header_element.find('p', class_='num-followers')
    store_ratings = root_element.find('div', class_='positive-fdbk')
    store_time_element = header_element.find('div', class_='store-time')
    store_name_element = header_element.find('h3', class_='store-name')

    if store_followers_element == None or store_ratings == None:
        print('Couldn\'t locate store data. Make sure you enter a valid link e.g https://www.aliexpress.com/item/2251832665683450.html')
        sys.exit()

    # get store elements
    product_title_element = root_element.find('h1', class_='product-title-text')
    product_ratings_element = root_element.find(class_='overview-rating-average')
    product_sold_element = root_element.find(class_='product-reviewer-sold')
    product_reviews_element = root_element.find(class_='product-reviewer-reviews')

    if product_ratings_element == None or product_sold_element == None:
        print('Couldn\'t locate product data. Try again.')
        sys.exit()

    # get price element
    product_price = root_element.find("span", class_="uniform-banner-box-price")
    product_fixed_price = root_element.find("span", class_="product-price-value")

    if product_price == None and product_fixed_price == None:
        print('Couldn\'t locate pricing data. Try again.')
        sys.exit()

    # hold the scraped data
    payload = {
        'store_followers': 0,
        'store_rating': 0,
        'store_name': '',
        'store_status': '',
        'product_title': '',
        'product_price': 0,
        'product_sold': 0,
        'product_ratings': 0,
        'avg_similar_price': 0
    }

    # get store informations
    if store_followers_element != None:
        payload['store_followers'] = aliexpress.getFollowersCount(store_followers_element.findChild().get_text())
    if store_ratings != None:
        payload['store_rating'] = aliexpress.getNumbers(store_ratings.get_text())
    if store_status_element != None:
        payload['store_status'] = store_status_element.findChild().get_text()
    if store_name_element != None:
        payload['store_name'] = store_name_element.findChild().get_text()
    if store_time_element != None:
        payload['store_time'] = store_time_element.findChild().get_text()


    # get product information
    if product_title_element != None:
        payload['product_title'] = product_title_element.get_text()
    if product_sold_element != None:
        payload['product_sold'] = aliexpress.getNumbers(product_sold_element.get_text())
    if product_ratings_element != None:
        payload['product_ratings'] = aliexpress.getNumbers(product_ratings_element.get_text())
    if product_reviews_element != None:
        payload['product_reviews'] = aliexpress.getNumbers(product_reviews_element.get_text())

    # two kind of price exist depending on the item
    fixed_price = 0
    average_price = 0

    if product_price != None:
        uniform_price = product_price.get_text()
        uniform_price = uniform_price.split("-")
        uniform_price[0] = aliexpress.getNumbers(uniform_price[0])
        if len(uniform_price) == 2:
            uniform_price[1] =  aliexpress.getNumbers(uniform_price[1])
        average_price = fn.mean(uniform_price)
    if product_fixed_price != None:
        fixed_price = aliexpress.getNumbers(product_fixed_price.get_text())
    
    # get the product price
    payload['product_price'] = fixed_price if fixed_price > 0 else average_price
    
    # each items has other similar items
    # and based on the pricing algorithm, it is neccessary
    # we check for similar items from other stores
    # and compare their average price with the price
    # of the main item
    search_title = payload['product_title'][:50]
    search_url = 'https://www.aliexpress.com/wholesale?catId=0&initiative_id=SB_20220825085630&origin=y&SearchText={}'.format(search_title)
    driver.get(search_url)

    # all similar items
    soup = BeautifulSoup(driver.page_source, "html.parser")
    similar_items_element = soup.find("div", class_="JIIxO")

    prices = []
    if similar_items_element != None:
        # nest down to the element holding the actual item
        items_elements = similar_items_element.find_all('a', class_='_3t7zg')
        i = 0
        for item_element in items_elements:
            # limit the element to iterate to 10
            i += 1
            if i >= 10:
                break
            # get the item title
            item_title_element = item_element.find('h1')
            item_title = item_title_element.get_text()
            # get the title similarity
            # and check if title is close enough
            similarity = fn.bleu_score(payload['product_title'], item_title_element.get_text())
            if (similarity >= 0.5):
                # print(item_title)
                price_wrapper_element = item_element.find('div', class_="mGXnE")
                price_elements = price_wrapper_element.findChildren()

                price = ""
                k = 1
                count =  len(price_elements)
                while k < count:
                    price += price_elements[k].get_text()
                    k += 1
                
                price = price.replace(',', '')
                prices.append(float(price))
                # print(price)
                # print()

    # if no similar prices found
    if len(prices) == 0:
        prices.append(payload['product_price'])
    # set the average similar price of related items
    payload['avg_similar_price'] = fn.mean(prices)

    # calculate the final score based on the 
    # store followers, ratings, product ratings,
    # product sold and also the comparative price
    follower_score = aliexpress.followersScore(payload['store_followers'])
    reputation_score = aliexpress.reputationScore(follower_score, payload['store_rating'])
    # automatic 25 points reputation to top brand
    if payload['store_status'].lower() == 'top brand':
        reputation_score = 25
    order_score = aliexpress.orderScore(payload['product_sold'], payload['product_ratings'], follower_score, reputation_score)
    product_score = aliexpress.productScore(payload['product_sold'], payload['product_ratings'], reputation_score)
    pricing_score = aliexpress.priceReputation(payload['product_price'], payload['avg_similar_price'], reputation_score)

    final_score = order_score + reputation_score + product_score + pricing_score

    print(payload)
    print(order_score, reputation_score, product_score, pricing_score)
    print("Product score", final_score)

finally:
    driver.quit()
