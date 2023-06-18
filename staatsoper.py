import asyncio
import os
import requests
import json
from bs4 import BeautifulSoup
from telegram import Bot
from requests.exceptions import RequestException

# Initialize Telegram Bot with your token and your chat_id
TELEGRAM_TOKEN = ""
CHAT_ID = ""
bot = Bot(token=TELEGRAM_TOKEN)

# URL to monitor
url = "https://www.staatsoper-berlin.de/de/extra/black-board/"

# Function to fetch the content of the website
def fetch_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        body = soup.body
        return soup if body else None
    except RequestException as e:
        print(f"Error fetching content: {e}")
        return None

async def check_for_updates():

    # Fetch the content and generate the hash
    url_content = fetch_content(url)

    # Find all the cards
    cards = url_content.find_all('li', {'class': 'card-list__item'})

    # This list will hold all of our cards
    data = []

    # Loop through each card
    for card in cards:
        # Extract the name and date
        name_date = card.find('li', {'class': 'list-inline__item'}).text.strip().split()
        name = ' '.join(name_date[:-1])
        date = name_date[-1]

        # Extract the email
        email = card.find('a', {'href': lambda x: x and 'mailto:' in x}).text.strip()

        # Extract the content
        content = card.find('div', {'class': 'card__body'}).text.strip().replace('\n', ' ')

        # Create a dictionary for this card
        card_data = {
            'name': name,
            'date': date,
            'email': email,
            'content': content
        }

        # Add the card to our list
        data.append(card_data)

    # Convert the list to JSON
    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    # Print the JSON
    #print(json_data)



    # Add the card to our list
    data.append(card_data)

    # Convert the list to JSON
    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    # Path to the JSON file where we will store the data
    json_file_path = "data.json"

    # If the file exists, read it and compare the old data with the new data
    if os.path.isfile(json_file_path):
        with open(json_file_path, 'r') as f:
            old_data = json.load(f)
            
        for new_entry in data:
            if new_entry not in old_data:
                print(f"New entry: {new_entry}")
                try:
                    await bot.send_message(chat_id=CHAT_ID, text=f"Staatsoper Black Board: {content}")
                except Exception as e:
                    print(f"Error sending Telegram message: {e}")


    # Whether the data is new or not, write the new data to the file
    with open(json_file_path, 'w') as f:
        f.write(json_data)

# Run the send_message function in the asyncio event loop
asyncio.run(check_for_updates())
