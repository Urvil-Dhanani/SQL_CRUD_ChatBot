# importing sql lite and will perform the operation 
# This process will happen in local machine only 

import sqlite3

# connecting to sqlite3 & creating database 
connection=sqlite3.connect(database="my_demo.db")

# creating a cursor object for CRUD operation
cursor=connection.cursor()


# creating a table with schema 
query_table_creation="CREATE TABLE STUDENT(NAME VARCHAR(25), CLASS VARCHAR(25), SECTION VARCHAR(25), MARKS INT);"
cursor.execute(query_table_creation)

# inserting some records 
cursor.execute("""INSERT INTO STUDENT VALUES('Urvil','Data Science','A',90); """)
cursor.execute("""INSERT INTO STUDENT VALUES('Krish','Data Science','A',90);""")
cursor.execute("""INSERT INTO STUDENT VALUES('John','Data Science','B',100);""")
cursor.execute("""INSERT INTO STUDENT VALUES('Mukesh','Data Science','A',86);""")
cursor.execute("""INSERT INTO STUDENT VALUES('Jacob','DEVOPS','A',50);""")
cursor.execute("""INSERT INTO STUDENT VALUES('Dipesh','DEVOPS','A',35);""")

# Display all the records 
print("The inserted records are:")
data=cursor.execute("SELECT * FROM STUDENT")  # here data will be a LIST of all the records 
for row in data:
    print(row)

# commit changes into the database
connection.commit()
connection.close()