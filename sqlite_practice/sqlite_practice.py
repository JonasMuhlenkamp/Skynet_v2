import sqlite3

connection = sqlite3.connect("testDB.db")
print("Connection successful!")

connection.execute('''DROP TABLE COMPANY''')

connection.execute('''CREATE TABLE COMPANY
            (ID INT PRIMARY KEY NOT NULL,
            NAME        TEXT    NOT NULL,
            AGE INT NOT NULL,
            ADDRESS TEXT NOT NULL,
            SALARY REAL);''')

connection.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
      VALUES (1, 'Paul', 32, 'California', 20000.00 )");

connection.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
      VALUES (2, 'Paul', 25, 'Texas', 18000.00 )");

connection.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
      VALUES (3, 'Perry', 23, 'Norway', 25000.00 )");

connection.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
      VALUES (4, 'Patricia', 25, 'Rich-Mond ', 65000.00 )");

connection.commit()

cursor = connection.execute("SELECT * FROM COMPANY WHERE SALARY > 18000 ORDER BY NAME, SALARY ASC")
for row in cursor:
    print("ID = " + str(row[0]))
    print("NAME = " + str(row[1]))
    print("AGE = " + str(row[2]))
    print("ADDRESS = " + str(row[3]))
    print("SALARY = " + str(row[4]) + "\n")

connection.close()