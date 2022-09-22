import mysql.connector


dataBase = mysql.connector.connect(
  host ="mysql",
  user ="root",
  passwd ="passwd",
  database = "recruitment"
)

# preparing a cursor object
cursorObject = dataBase.cursor()
# creating database
# cursorObject.execute("CREATE DATABASE IF NOT EXISTS recruitment")
try:
    cursorObject.execute("DROP TABLE skills")
except:
    pass
try:
    cursorObject.execute("DROP TABLE programmers")
except:
    pass

dataBase.commit()
