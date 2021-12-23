import requests
import json
import csv
import os
import time
from datetime import datetime

#An important function that will update the TCGPlayer API bearer token in the system variables.
#This is needed because the token expires every two weeks.
def update_bearer():
    #Access the keys that allow us to get a bearer token in the first place (they are stored as environment variables)
    PUBLIC_KEY = os.environ.get('TCG_PUBLIC_KEY')
    PRIVATE_KEY = os.environ.get('TCG_PRIVATE_KEY')

    #Set up the headers and keys for the post request 
    headers = {"User-Agent": "Nautilus", "From": "nautilus.application@gmail.com", "application": "x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials", "client_id": PUBLIC_KEY, "client_secret": PRIVATE_KEY}

    #Request the token
    response = requests.post("https://api.tcgplayer.com/token", headers=headers, data=data)
    response_dict = json.loads(response.text)

    #Save the token in the environment variables
    BEARER_TOKEN = response_dict["access_token"]
    expire_date = response_dict[".expires"]
    os.environ['TCG_BEARER_TOKEN'] = BEARER_TOKEN
    print("Update successful.  Token will expire on " + str(expire_date))
    return BEARER_TOKEN

#This function grabs cards, 100 at a time, and finds the price data for them on TCGPlayer
def get_tcg_price_data(foil_dict, id_array, export_file, read_mode, bearer):

    # grab identifiers from environment variables
    PUBLIC_KEY = os.environ.get('TCG_PUBLIC_KEY')
    PRIVATE_KEY = os.environ.get('TCG_PRIVATE_KEY')

    #will expire Thu Jul 30 16:15:15 GMT
    BEARER_TOKEN = bearer

    if read_mode != "a":
        open(export_file, "w").close()
    
    foil_dictionary = foil_dict
    num_cards = len(id_array)
    #print(num_cards)
    card_count = 0
    cards_idd = 0
    response_dict = ""
    first_run = True
    run_count = -1
    while card_count + 1 <= num_cards:
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

            headers = {"User-Agent": "Nautilus", "From": "nautilus.application@gmail.com", "accept": "application/json", "authorization": "bearer " + BEARER_TOKEN}

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

            headers = {"User-Agent": "Nautilus", "From": "nautilus.application@gmail.com", "accept": "application/json", "authorization": "bearer " + BEARER_TOKEN}

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

update_bearer()