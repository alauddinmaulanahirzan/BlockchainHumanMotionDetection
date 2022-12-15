# Firebase Section
from firebase_admin import db
import firebase_admin
from firebase_admin import credentials
from google.cloud import storage
# Additional Section
import platform

class FirebaseHandler:
    def connectDB():
        databaseURL_1 = "https://iot-db-b4768-default-rtdb.asia-southeast1.firebasedatabase.app/"
        databaseURL_2 = "https://iot-db-2-b22fb-default-rtdb.asia-southeast1.firebasedatabase.app/"
        cred_1 = credentials.Certificate("iot-db-adminsdk.json")
        cred_2 = credentials.Certificate("iot-db-2-adminsdk.json")
        app_primary = firebase_admin.initialize_app(cred_1,{'databaseURL':databaseURL_1})
        app_secondary = firebase_admin.initialize_app(cred_2, {'databaseURL': databaseURL_2}, name='Secondary')
        ref_1 = db.reference("/",app=app_primary)
        ref_2 = db.reference("/",app=app_secondary)
        return ref_1,ref_2

    def connectThirdDB():
        databaseURL_3 = "https://iot-db-3-default-rtdb.asia-southeast1.firebasedatabase.app/"
        cred_3 = credentials.Certificate("iot-db-3-adminsdk.json")
        app_tertiary = firebase_admin.initialize_app(cred_3, {'databaseURL': databaseURL_3}, name='Tertiary')
        ref_3 = db.reference("/",app=app_tertiary)
        return ref_3

    def insertData(ref_1,ref_2,id,block):
        # Set Machine Key
        target_platform = platform.uname().node.lower()
        # Set Target Block ID
        target_blockid = "B_"+str(id).zfill(4)
        # Set Target Reference
        target_ref_1 = ref_1.child(target_platform).child(target_blockid)
        target_ref_2 = ref_2.child(target_platform).child(target_blockid)
        # Insert
        target_ref_1.set({"01 Previous":block.previous,
                        "02 Data":block.data,
                        "03 Hash":block.hash})

        target_ref_2.set({"01 Previous": block.previous,
                          "02 Data": block.data,
                          "03 Hash": block.hash})

    def connectBucket():
        storage_client_1 = storage.Client.from_service_account_json('iot-db-adminsdk.json')
        storage_client_2 = storage.Client.from_service_account_json('iot-db-2-adminsdk.json')
        bucket_1 = storage_client_1.get_bucket("iot-db-b4768.appspot.com",timeout=None)
        bucket_2 = storage_client_2.get_bucket("iot-db-2-b22fb.appspot.com", timeout=None)
        return bucket_1,bucket_2

    def uploadData(bucket_1,bucket_2,byte_data,identifier):
        blob_1 = bucket_1.blob(identifier)          # Identifier from UUID
        blob_1.upload_from_string(byte_data)      # Data in Byte
        blob_2 = bucket_2.blob(identifier)  # Identifier from UUID
        blob_2.upload_from_string(byte_data)  # Data in Byte
        if(blob_1.exists() == True and blob_2.exists() == True):
            return True
        else:
            return False

    def downloadData(bucket_1,bucket_2,identifier):
        data = None
        blob_1 = bucket_1.blob(identifier)         # Identifier from DB
        blob_2 = bucket_2.blob(identifier)  # Identifier from DB
        # Download Data
        if(blob_1.exists() == True and blob_2.exists() == True):
            blob_1.reload()
            data = blob_1.download_as_string()
            return data,True
        else:
            return data,False

    def checkData(bucket_1,bucket_2,identifier):
        blob_1 = bucket_1.blob(identifier)       # Identifier from DB
        blob_2 = bucket_2.blob(identifier)  # Identifier from DB
        if(blob_1.exists() == True and blob_2.exists() == True):
            return True
        else:
            return False

    def getDataSize(bucket_1,bucket_2,identifier):
        blob_1 = bucket_1.blob(identifier)       # Identifier from DB
        blob_2 = bucket_2.blob(identifier)  # Identifier from DB
        if(blob_1.exists() == True and blob_2.exists() == True):
            blob_1 = bucket_1.get_blob(identifier)
            size = blob_1.size
            return size
        else:
            return 0