# Q11. Write a Python program to connect to an SQLite3 database, create a table, insert data, and 
# fetch data. 


import sqlite3

# 1. Connect to SQLite database (creates file if it doesn’t exist)
conn = sqlite3.connect("mydatabase.db")

# 2. Create a cursor object (used to execute SQL commands)
cursor = conn.cursor()

# 3. Create a table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    course TEXT
)
""")

# 4. Insert data into the table
cursor.execute("INSERT INTO students (name, age, course) VALUES (?, ?, ?)", ("Alice", 21, "Python"))
cursor.execute("INSERT INTO students (name, age, course) VALUES (?, ?, ?)", ("Bob", 22, "Java"))
cursor.execute("INSERT INTO students (name, age, course) VALUES (?, ?, ?)", ("Charlie", 20, "C++"))

# 5. Commit the changes (save to database)
conn.commit()

# 6. Fetch data from the table
cursor.execute("SELECT * FROM students")
rows = cursor.fetchall()

# 7. Print fetched data
print("Student Records:")
for row in rows:
    print(row)

# 8. Close the connection
conn.close()
