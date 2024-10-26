import requests
from bs4 import BeautifulSoup
import re
import datetime
from db import Offer

class Parser:
    base = "https://avito.ru"


    def get_first(self, url):
        try:
            # Send a GET request to the provided URL
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            
            # Parse the response text with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the first DIV tag with data-marker="item"
            item_div = soup.find('div', attrs={'data-marker': 'item'})
            if item_div:
                # Find the A tag with data-marker="item-title" inside the DIV
                item_title = item_div.find('a', attrs={'data-marker': 'item-title'})
                if item_title:
                    # Extract params
                    id = int(item_div['data-item-id'])
                    title = item_title.text.strip()
                    href = self.base + item_title['href']

                    description_meta = item_div.find('meta', attrs={'itemprop': 'description'})
                    description = description_meta['content'] if description_meta else None

                    date_p = item_div.find('p', attrs={'data-marker': 'item-date'}).text
                    date = self.parse_date(date_p)

                    price = item_div.find('meta', attrs={'itemprop': 'price'})
                    price = price['content'] if price else None

                    if description:
                        description = re.sub(r'\n+', '\n', description).strip()

                    return Offer(id=id,title=title,link=href,desc=description,date=date,price=price)
            return None  # Return None if no item is found
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None


    def parse_date(self, date_string):
        td = {"недел":10080,
                "дн":1440,
                "день":1440,
                "час":60,
                "минут":1}
        now = datetime.datetime.now()

        match = re.match(r'^\d+ (недел|дн|день|час|минут)',date_string)
        print(match)
        if match:
            match = match.group(0)
            match = match.split(" ")
            minutes = int(match[0]) * td[match[1]] 
            timedelta = datetime.timedelta(minutes=minutes)
            return now - timedelta
        else:
            print(f'date_string: {date_string} is bigger than a month\nsetting time to 1 month ago')
            return now - datetime.timedelta(days=30)


