**Blockchain-powered Human Motion Detection**

**This project contains many codes used for OpenCV-powered Human Motion Detection. Basically, this project is a Human Motion Detection but We stored all the data in a shape of Blockchain**

**We used:**
- *Python 3.9.2* for compatibility with Raspberry Pi's Python
- *OpenCV* for the detection (either pip:*opencv-python* or *python3-opencv*)
- *Pycryptodome* for RSA Encrption and Decryption
- *Firebase* for storing data in a Blockchain (it is easier for me to design rather than SQL-type)
- *Python-Telegram-Bot* for On Demand Query
- *YOLO-coco Tiny*

**Dependencies refer to requirements.txt**

**This Project consists of:**
- **Blockchain.py** is the standard template for this project Blockchain
- **CameraHandle.py** has the role to manage the detection, capture, and recording
- **FirebaseHandler.py** has the role to handle the connection and data to Firebase, and Google Storage
- **MainApp.py** is the main program no need any argument
- **MainFetch.py** activates Telegram Bot. Now no longer need user id
- **RSAKeygen.py** generates key for encryption and decryption (default 2048-bit)
- **Telemetry.py** generates benchmark data during query to Firebase.
- **VideoChecking.py** will retrieve all data from Firebase

**This project is a research project funded by LPPM Universitas Semarang, Indonesia.**

**Citation Coming Soon**

** EDIT: Commit Signed **
