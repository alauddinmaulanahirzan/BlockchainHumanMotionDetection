from FirebaseHandler import *
from Blockchain import *
import cv2
import imutils
import numpy
import numpy as np
import os
import csv

def getData(ref,bucket,start):
    start = int(start)
    db = ref.get()
    if(db is not None):
        for machine in db.keys():
            blocks = ref.child(machine).get()
            for block in blocks.keys():
                id = int(block.split("_")[1])
                if(id>=start):
                    print(f"==> Downloading Video From '{block}'-'{machine}'",end="",flush=True)
                    # Get Date and Time
                    block_data = ref.child(machine).child(block).get()
                    # Retrieve Data
                    video_id = block_data['02 Data']['0-0 Data']
                    # Download Data
                    video_data,status = FirebaseHandler.downloadData(bucket,Blockchain.decryptMessage(str(video_id)))
                    print(" > [SUCCESS]")
                    # Write as File
                    filename = f"Records/Video_{block}_{machine}.avi"
                    print("==> Writing to File",end="",flush=True)
                    file_out = open(filename,"wb")
                    file_out.write(video_data)
                    file_out.close()
                    print(" > [SUCCESS]")

def getMachineData(ref,bucket,machine,start):
    start = int(start)
    db = ref.child(machine).get()
    if(db is not None):
        for block in db.keys():
            ref,bucket = connectFirebase()
            id = int(block.split("_")[1])
            if(id>=start):
                print(f"==> Downloading Video From '{block}'-'{machine}'",end="",flush=True)
                # Get Date and Time
                block_data = ref.child(machine).child(block).get()
                # Retrieve Data
                video_id = block_data['02 Data']['0-0 Data']
                # Download Data
                video_data,status = FirebaseHandler.downloadData(bucket,Blockchain.decryptMessage(str(video_id)))
                print(" > [SUCCESS]")
                # Write as File
                filename = f"Records/Video_{block}_{machine}.avi"
                print("==> Writing to File",end="",flush=True)
                file_out = open(filename,"wb")
                file_out.write(video_data)
                file_out.close()
                print(" > [SUCCESS]")

def connectFirebase():
    print("==> Connecting to Firebase",end="",flush=True)
    ref = FirebaseHandler.connectDB() # Connect Once
    print(" > [CONNECTED]")
    print("==> Connecting to Google Storage",end="",flush=True)
    bucket = FirebaseHandler.connectBucket() # Connect Google Storage
    print(" > [CONNECTED]")
    return ref,bucket

def getDiffVideos(files):
    avgs = {}
    # Read File
    for file in files:
        # Parameter
        frame1 = None
        frame2 = None
        sum = 0
        average = 0
        frames = []
        filename = str.split(file,"/")[5]
        filename = str.split(filename,".")[0]
        print(f"==> Calculating {filename}",end="",flush=True)
        cap = cv2.VideoCapture(file)
        while(True):
            ret, frame = cap.read()
            if(frame is not None):
                frame_gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                frame_gray = cv2.GaussianBlur(frame_gray, (25, 25), 0)
                frames.append(frame_gray)
            else:
                break
        # Set Resolution from Sample
        height = frames[0].shape[0]
        width = frames[0].shape[1]
        res = np.zeros((height, width), dtype=np.uint8)
        # Get Difference
        for frame in frames:
            if(frame1 is None):
                frame1 = frame
            else:
                frame2 = frame
                deltaframe = cv2.absdiff(frame1,frame2)
                threshold = cv2.threshold(deltaframe, 0, 255, cv2.THRESH_BINARY)[1]
                threshold = cv2.dilate(threshold,None)
                countour = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                frame1 = frame2
                if(countour[1] is not None):
                    percentage = (countour[0][0].size/len(res))*100
                else:
                    percentage = (len(data[0])/len(res))*100
                sum += percentage
        average = sum/len(frames)
        avgs.update({file:average})
        print(f" > [DONE]")
    return avgs

def getFiles():
    print("==> Listing All Files",end="",flush=True)
    files = []
    for dirname, dirnames, filenames in os.walk('/media/maulana/QemuVM/New-Records/'):
        for filename in filenames:
            # Operasi File
            file = os.path.join(dirname, filename)
            files.append(file)
    print(" > [DONE]")
    return files

def writeCSV(avgs):
    print("==> Saving to File",end="",flush=True)
    filename = "benchmark_diff.csv"
    counter = 1
    if os.path.isfile(filename):
        os.remove(filename)
    # Set Header CSV
    header = ["No","File","Difference"]
    with open(filename,"w") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for key in avgs.keys():
            writer.writerow([counter,key,avgs[key]])
            counter += 1
    print(" > [DONE]")

def main():
    files = []
    start = 1
    machine = "pi-ircam2-usm"
    # ref,bucket = connectFirebase()
    # getData(ref,bucket,start)
    # getMachineData(ref,bucket,machine,start)
    files = getFiles()
    avgs = getDiffVideos(files)
    writeCSV(avgs)

if __name__ == '__main__':
    main()
