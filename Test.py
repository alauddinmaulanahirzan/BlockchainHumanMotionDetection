
# Multi Ref Query Test
from firebase_admin import db
import firebase_admin
from firebase_admin import credentials

def connectDB():
    databaseURL_1 = "https://iot-db-b4768-default-rtdb.asia-southeast1.firebasedatabase.app/"
    databaseURL_2 = "https://iot-db-2-b22fb-default-rtdb.asia-southeast1.firebasedatabase.app/"
    cred_1 = credentials.Certificate("iot-db-adminsdk.json")
    cred_2 = credentials.Certificate("iot-db-2-adminsdk.json")
    app_primary = firebase_admin.initialize_app(cred_1, {'databaseURL': databaseURL_1})
    app_secondary = firebase_admin.initialize_app(cred_2, {'databaseURL': databaseURL_2}, name='Secondary')
    ref_1 = db.reference("/", app=app_primary)
    ref_2 = db.reference("/", app=app_secondary)

    ref_1.set("Data")
    ref_2.set("Data")

def readFile():
    while True:
        try:
            file = open(".gitignore", "r")
            print(file)
            break
        except:
            print("File Not Found")

def compare():
    id = "B_"+str(1).zfill(4)
    id=="B_0001"

readFile()