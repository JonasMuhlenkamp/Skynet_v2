import sqlite3
import csv
import requests, json

#We will be defining a 'Database' class
class Database:
    
    #The initialization method of the class
    def __init__(self, db):

        #Connect to the database, establish a cursor, and create the cards table.
        self.conn = sqlite3.connect(db)
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS cards (id INTEGER PRIMARY KEY, cardname TEXT NOT NULL, setname TEXT, setcode TEXT NOT NULL, collector_num INT NOT NULL, color TEXT, colorkey INT NOT NULL, price REAL, daily_change REAL, weekly_change REAL)")

    #Grabbing database members that match a given name
    def name_fetch(self, cardname=""):

        #The actul SQL command to grab the datas :)
        self.cursor.execute("SELECT * FROM cards WHERE cardname LIKE ?", ('%' + cardname + '%',))

        #Convert the data from SQL to a list object
        rows = self.cursor.fetchall()
        return rows

    #Inserts rows one at a time from an array object: [cardname, set, setcode, color, colorkey]
    def insert_simple(self, inputs):
        
        #Unpack the inputs array
        cardname = inputs[0]
        setname = inputs[1]
        setcode = inputs[2]
        collector_num = inputs[3]
        color = inputs[4]
        colorkey = inputs[5]

        #Insert the row in SQL-speak
        self.cursor.execute("INSERT INTO cards (cardname,setname,setcode,collector_num,color,colorkey) \
      VALUES (?, ?, ?, ?, ?, ?)", (cardname, setname, setcode, collector_num, color, colorkey))

        #Commit the change to the database
        self.conn.commit()

    #Insert card objects from a .csv file
    def insert_csv(self, input_csvpath):
        
        #Open the file
        with open(input_csvpath, mode='r') as csv_file:
            
            #Start the reader
            fieldnames = ['cardname', 'setname', 'setcode', 'collector_num', 'color', 'colorkey']
            reader = csv.reader(csv_file)#, fieldnames=fieldnames)

            #Loop over the rows in the file
            row_count = 0 
            for row in reader:
                inputs = []
                if row_count > 0:
                    for i in range(0, len(row)):
                        inputs.append(row[i])

                    #Input each row individually
                    self.insert_simple(inputs)
                
                row_count += 1
                
        #Commit the changes
        self.conn.commit()

    #Deletes rows one at a time based on an array object: [cardname, setcode, collector_num]
    def delete_simple(self, inputs):
    
        #Unpack the inputs array
        cardname = inputs[0]
        setcode = inputs[1]
        collector_num = inputs[2]

        #Find all ids that match the cardname and set
        ids = self.cursor.execute("SELECT id FROM cards WHERE cardname=? AND setcode=? AND collector_num=?", (cardname, setcode, collector_num))

        for id_num in ids:
            self.cursor.execute("DELETE FROM cards WHERE id=?", id_num)

        #Commit the change to the database
        self.conn.commit()

    #Delete card objects based on a .csv file
    def delete_csv(self, input_csvpath):
        
        #Open the file
        with open(input_csvpath, mode='r') as csv_file:
            
            #Start the reader
            fieldnames = ['cardname', 'setname', 'setcode', 'collector_num', 'color', 'colorkey']
            reader = csv.reader(csv_file)#, fieldnames=fieldnames)

            #Loop over the rows in the file
            row_count = 0 
            for row in reader:
                inputs = []
                if row_count > 0:
                    inputs.append(row[0])
                    inputs.append(row[2])
                    inputs.append(row[3])

                    #Input each row individually
                    self.delete_simple(inputs)
                
                row_count += 1
                
        #Commit the changes
        self.conn.commit()

#temp function for simplicity in filling .db for testing
def grab_colors(api_card):

    colors = api_card["colors"]
    color = ""
    colorkey = 0
    if len(colors) > 1:
        color = "Multi"
        colorkey = 7
    elif str(api_card["type_line"]).lower().__contains__("land"):
        color = "Land"
        colorkey = 1
    elif len(colors) == 0:
        color = "Colorless"
        colorkey = "8"
    else:
        if colors[0] == "W":
            color = "White"
            colorkey = 2
        elif colors[0] == "U":
            color = "Blue"
            colorkey = 3
        elif colors[0] == "B":
            color = "Black"
            colorkey = 4
        elif colors[0] == "R":
            color = "Red"
            colorkey = 5
        elif colors[0] == "G":
            color = "Green"
            colorkey = 6

    return color, colorkey

#temp nonsense for filling .db quickly
# url = "https://api.scryfall.com/cards/search?q=game:paper"
# response = requests.get(url)
# response_dict = json.loads(response.text)

# with open("sqlite_practice/cards_test1.csv", mode="w", newline="") as csv_file:

#     fieldnames = ['cardname', 'setname', 'setcode', 'collector_num', 'color', 'colorkey']
#     writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#     writer.writeheader()
    
#     for card in response_dict["data"]:
        
#         cardface = ""
#         try:
#             cardface = card["card_faces"][0]
#         except:
#             cardface = card
        
#         color, colorkey = grab_colors(cardface)

#         writer.writerow({'cardname': card['name'], 'setname': card['set_name'], 'setcode': card['set'], 'collector_num': card['collector_number'], 'color': color, 'colorkey': colorkey})



cards = Database("sqlite_practice/testDB.db")
cards.insert_csv("sqlite_practice/cards_test1.csv")
# cards.delete_simple(["Abandoned Sarcophagus", "c20", "236"])
card1 = cards.name_fetch("Abandoned Sarcophagus")
for row in card1:
    print(row)

