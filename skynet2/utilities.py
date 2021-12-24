import requests
import json
import csv
import os
import time
from datetime import datetime

# Global
# Access the keys that allow us to get a bearer token in the first place (they are stored as environment variables)
_PUBLIC_KEY = os.environ.get('TCG_PUBLIC_KEY')
_PRIVATE_KEY = os.environ.get('TCG_PRIVATE_KEY')
_BEARER_TOKEN = os.environ.get('TCG_BEARER_TOKEN')

#An important function that will update the TCGPlayer API bearer token in the system variables.
#This is needed because the token expires every two weeks.
def update_bearer():
    
    # Allowing changes to a global var within this function
    global _BEARER_TOKEN

    #Set up the headers and keys for the post request 
    headers = {"User-Agent": "Nautilus", "From": "nautilus.application@gmail.com", "application": "x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials", "client_id": _PUBLIC_KEY, "client_secret": _PRIVATE_KEY}

    #Request the token
    response = requests.post("https://api.tcgplayer.com/token", headers=headers, data=data)
    response_dict = json.loads(response.text)

    #Save the token in the environment variables
    _BEARER_TOKEN = response_dict["access_token"]
    expire_date = response_dict[".expires"]
    os.environ['TCG_BEARER_TOKEN'] = _BEARER_TOKEN
    print("Update successful.  Token will expire on " + str(expire_date))

#This function grabs cards, 100 at a time, and finds the price data for them on TCGPlayer
def get_tcg_price_data(foil_dict, id_array, export_file, read_mode):
    
    foil_dictionary = foil_dict
    num_cards = len(id_array)
    #print(num_cards)
    card_count = 0
    response_dict = ""
    first_run = True
    run_count = -1
    while card_count < num_cards:
        if card_count % 100 == 0:
            
            productID_string = ""
            for i in range(0, 100):
                #print(card_count + i)
                if card_count + i >= num_cards:
                    break
                else:
                    productID_string = productID_string + str(id_array[card_count + i]) + ","

            productID_string = productID_string[:len(productID_string) - 1]

            base_url = "https://api.tcgplayer.com/pricing/product/"
            url = base_url + productID_string

            headers = {"User-Agent": "Nautilus", "From": "nautilus.application@gmail.com", "accept": "application/json", "authorization": "bearer " + _BEARER_TOKEN}

            response = requests.request("GET", url, headers=headers)
            response_dict = json.loads(response.text)

            run_count += 1
            #jprint(response_dict)

        elif (card_count - run_count * 100) % 99 == 0: #weird glitch reported 9/26/21 where after row 900 it switches to only running to 99
            productID_string = ""
            for i in range(0, 99):
                #print(card_count + i)
                if card_count + i >= num_cards:
                    break
                else:
                    productID_string = productID_string + str(id_array[card_count + i]) + ","

            productID_string = productID_string[:len(productID_string) - 1]

            base_url = "https://api.tcgplayer.com/pricing/product/"
            url = base_url + productID_string

            headers = {"User-Agent": "Nautilus", "From": "nautilus.application@gmail.com", "accept": "application/json", "authorization": "bearer " + _BEARER_TOKEN}

            response = requests.request("GET", url, headers=headers)
            response_dict = json.loads(response.text)
        #id: {directLow: xx.xx, market: xx.xx, lo: xx.xx, mid: xx.xx, hi: xx.xx}
        cards_in_run = 0
        with open(export_file, mode="a", newline="") as csv_file:
        
            fieldnames = ["tcgplayer_id", "directLow", "market", "low", "mid"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            
            if read_mode != "a" and first_run == True:
                writer.writeheader()
                first_run = False
            
            directLow = 0
            market = 0
            low = 0
            mid = 0
            # jprint(response_dict)
            for product in response_dict["results"]:

                product_ID = product["productId"]
                  
                if product["subTypeName"] == "Foil":
                    if(foil_dictionary[product_ID] == "TRUE"):
                        cards_in_run += 1
                    product_ID = str(product_ID) + " (Foil)"
                else:
                    if foil_dictionary[product_ID] == "FALSE":
                        cards_in_run += 1
                    product_ID = str(product_ID) + " (Nonfoil)"
                
                directLow = product["directLowPrice"]
                market = product["marketPrice"]
                low = product["lowPrice"]
                mid = product["midPrice"]
                writer.writerow({"tcgplayer_id": product_ID, "directLow": directLow, "market": market,
                    "low": low, "mid": mid})
                #print(card_count)
                #print(cards_in_run)
                
        # print(cards_in_run)
        print(run_count)
        card_count += cards_in_run
        print(card_count)
    time.sleep(10)

# Slightly adjusted price grabber, streamlined for grabbing all prices, period
def get_all_tcg_prices():

    # Array of TCG Ids
    tcg_ids = []

    # Open the id file and pull the ids out into the id array
    id_file = open("tcg_ids.csv", mode = "r")
    fieldnames = ["cardname", "setId", "tcgId"]
    id_reader = csv.DictReader(id_file, fieldnames=fieldnames)
    for row in id_reader:
        tcg_ids.append(row["tcgId"])
    id_file.close()

    # Some config data from the ids
    num_cards = len(tcg_ids)

    # Setting up the price .csv
    price_file = open("tcg_prices.csv", mode="w", newline="")
    fieldnames = ["tcgId", "foil", "directLow", "market", "low", "mid", "high"]
    price_writer = csv.DictWriter(price_file, fieldnames=fieldnames)
    price_writer.writeheader()

    # Current date and time saved in file
    time = datetime.now().strftime("%y-%m-%d %H:%M:%S")
    price_writer.writerow({"tcgId": time, "foil": "", "directLow": "", "market": "", "low": "", "mid": "", "high": ""})

    # For each set of 100 ids, create a productId string and send it into the TCG API for pricing data
    # Then save the pricing data in a new .csv file 
    card_count = 0
    while card_count < num_cards:

        # Create the productID string
        productID_string = ""
        for i in range(0, 99):

            if card_count + i >= num_cards:
                break
            else:
                productID_string = productID_string + str(tcg_ids[card_count + i]) + ","

        productID_string = productID_string[:len(productID_string) - 1]

        # Build the request url
        base_url = "https://api.tcgplayer.com/pricing/product/"
        url = base_url + productID_string

        # Headers for request (permissions so that TCG lets us in)
        headers = {"User-Agent": "Nautilus", "From": "nautilus.application@gmail.com", "accept": "application/json", "authorization": "bearer " + _BEARER_TOKEN}

        # Submit request
        response = requests.request("GET", url, headers=headers)
        response_dict = json.loads(response.text)

        # Process the request
        for product in response_dict["results"]:
            # jprint(product)
            # Store foil as a boolean for convenience
            printing = product["subTypeName"]
            foil = False
            if printing == "Foil": foil = True

            # All the other data    
            tcg_id = product["productId"]
            directLow = product["directLowPrice"]
            market = product["marketPrice"]
            low = product["lowPrice"]
            mid = product["midPrice"]
            high = product["highPrice"]

            # TCG has slots even for cards w/o prices (bc they don't exist in either foil or nonfoil),
            # so we don't want to waste space on those
            # I considered doing this but it doesn't affect the time much and there might be a few relevant cards that get lost
            #if directLow == None and market == None and low == None and mid == None and high == None: continue
            #else:
            price_writer.writerow({"tcgId": tcg_id, "foil": foil, "directLow": directLow, "market": market,
                    "low": low, "mid": mid, "high": high})

        # Increase card count by 100
        card_count += 100




# For pretty printing json data
def jprint(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)
    return text

# Grabbing all card names and their TCG IDs
def get_tcg_card_ids():

    # Set up request url from TCG's API
    base_url = "https://api.tcgplayer.com/catalog/products?categoryId=1&productTypes=Cards&limit=100&offset="
    processed_cards = 0
    total_cards = 1 # this will be set based on the first request's return
    first_loop = True # flag to indicate that the first loop is happening

    # Open the csv file for storage and set up the writer
    csv_file = open("tcg_ids.csv", mode="w", newline="")
    fieldnames = ["cardname", "setId", "tcgId"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    # We will loop over every card in the API
    while processed_cards < total_cards:

        # Construct the URL for the call
        url = base_url + str(processed_cards)

        # Headers for request (permissions so that TCG lets us in)
        headers = {"User-Agent": "Nautilus", "From": "nautilus.application@gmail.com", "accept": "application/json", "authorization": "bearer " + _BEARER_TOKEN}

        # Submit request
        response = requests.request("GET", url, headers=headers)
        response_dict = json.loads(response.text)

        # Grab limiting number of cards from the first call, then don't do it again
        if first_loop: 
            total_cards = response_dict["totalItems"]
            # jprint(response_dict)
            first_loop = False

        # For each card in the request, count it and grab some info from it
        card_count = 0
        for card in response_dict["results"]:

            # Save info as variables
            cardname = card["name"]
            setId = card["groupId"]
            tcgId = card["productId"]

            # Store card data in a .csv file
            writer.writerow({"cardname": cardname, "setId": setId, "tcgId": tcgId})
            
            # print(card["name"] + " (" + str(card["groupId"]) + "): " + str(card["productId"]))
            card_count += 1
        
        # Increase the offset
        processed_cards += card_count
        # print(processed_cards)

update_bearer()
current_time = datetime.now()
get_all_tcg_prices()
finished_time = datetime.now()
run_time = finished_time - current_time
print(run_time)