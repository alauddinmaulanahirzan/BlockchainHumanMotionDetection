# Blockchain Section
from Blockchain import Blockchain
# Firebase Section
from FirebaseHandler import FirebaseHandler
# Camera Section
from CameraHandler import *
# Telemetry Section
from Telemetry import *
# Telegram Handler
from TelegramHandler import *
# Additional Section
import os
import time
from datetime import datetime
import argparse

# Hyper Parameters
ref_1 = None
ref_2 = None
bucket_1 = None
bucket_2 = None
process = None
record_lock = False
counter = 0
hash = None
id = 1

ap = argparse.ArgumentParser()
args = vars(ap.parse_args())
botHandler = TelegramHandler()

def runDetection():
    global record_lock,counter,id
    # Main Parameters
    frame1 = None
    motion = False
    timer = 0

    # Detection Start
    print("==> Opening Camera",end="",flush=True)
    camera = CameraHandler.initCamera() # Open Camera
    print(" > [DONE]")
    print("\n==> Detection > [READY]")
    # Start Loop
    while(True):
        # Cooldown Timer
        if(id>99999):
            break
        elif(record_lock == True):
            if(timer==5):
                print("\n==> Lock Released")
                print("==> Reseting Record Parameters",end="",flush=True)
                record_lock = False
                timer = 0
                frame1 = None
                motion = False
                print(" > [DONE]")
                print("==> Detection > [RESTARTED]")
                print("\n==> Detection > [READY]")
            else:
                print(f"====> Releasing Lock in {5-timer}s",end="\r")
                timer += 1
                time.sleep(1)
        elif(record_lock == False):
            start_milli = current_milli_time()
            percentage  = 0
            # Detect Motion
            frame = CameraHandler.getFrame(camera)
            if(frame1 is None):
                frame1 = frame
            else:
                frame2 = frame
                motion,percentage = doCompare(frame1,frame2)
                frame1 = frame2
            if(motion==True):
                print("\n==> Motion Detected")
                # Record Video
                base_filename = "Records/Data_" + str(datetime.now().strftime("%d-%m-%Y_%H.%M.%S"))
                filename_video = base_filename + "_video.avi"
                doRecord(filename_video,frame,camera,id)
                # Check Person Data => Frame, Object, Acc, Proc time
                print("====>> Recognizing Object", end="", flush=True)
                filename_image = base_filename + "_image.jpg"
                frame, label, accuracy, proc_time = doObjectDetect(frame,filename_image)
                # Upload Data
                doUpload(base_filename,start_milli,percentage,id,label,accuracy,proc_time)
                # Lock
                counter += 1
                record_lock = True
                id += 1

    print("\n==> Closing Camera",end="",flush=True)
    CameraHandler.closeCamera(camera)
    print(" > [DONE]")
    print("==> Detection Finished\n")

def doCompare(frame1,frame2):
    # Do Comparison
    height = frame2.shape[0]
    width = frame2.shape[1]
    res = np.zeros((height, width), dtype=np.uint8)
    # Convert to Grayscale
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    # Denoising
    gray1 = cv2.GaussianBlur(gray1, (25, 25), 0)
    gray2 = cv2.GaussianBlur(gray2, (25, 25), 0)
    # Find Delta
    deltaframe = cv2.absdiff(gray1,gray2)
    threshold = cv2.threshold(deltaframe, 25, 255, cv2.THRESH_BINARY)[1]
    threshold = cv2.dilate(threshold,None)
    countour = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Find Difference Percentage
    if(countour[1] is not None):
        percentage = (countour[0][0].size/len(res))*100
    else:
        percentage = (len(countour[0])/len(res))*100
    if(countour[1] is None):
        motion = False
    else:
        motion = True
    return motion,percentage

def doObjectDetect(frame,filename_image):
    obj = None
    accuracy = 0
    proc_time = None
    human = 0
    (W, H) = (None, None)

    # Load YOLO COCO
    labelsPath = os.path.sep.join(["yolo-coco", "coco.names"])
    LABELS = open(labelsPath).read().strip().split("\n")
    COLORS = np.random.randint(0, 255, size=(len(LABELS), 3), dtype="uint8")

    # derive the paths to the YOLO weights and model configuration
    weightsPath = os.path.sep.join(["yolo-coco", "yolov3.weights"])
    configPath = os.path.sep.join(["yolo-coco", "yolov3.cfg"])

    # load our YOLO object detector trained on COCO dataset (80 classes) and determine only the *output* layer names that we need from YOLO
    net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
    ln = net.getLayerNames()
    ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()]

    if W is None or H is None:
        (H, W) = frame.shape[:2]

    blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    start = time.time()
    layerOutputs = net.forward(ln)
    end = time.time()
    proc_time = end - start

    # initialize our lists of detected bounding boxes, confidences, and
    # class IDs, respectively
    boxes = []
    confidences = []
    classIDs = []

    # loop over each of the layer outputs
    for output in layerOutputs:
        # loop over each of the detections
        for detection in output:
            # extract the class ID and confidence (i.e., probability) of
            # the current object detection
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]

            # filter out weak predictions by ensuring the detected
            # probability is greater than the minimum probability
            if confidence > 0.5: # Default 0.5
                # scale the bounding box coordinates back relative to the
                # size of the image, keeping in mind that YOLO actually
                # returns the center (x, y)-coordinates of the bounding
                # box followed by the boxes' width and height
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")

                # use the center (x, y)-coordinates to derive the top and
                # and left corner of the bounding box
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                # update our list of bounding box coordinates, confidences,
                # and class IDs
                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)

    # apply non-maxima suppression to suppress weak, overlapping bounding
    # boxes
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.5,0.3)

    # ensure at least one detection exists
    if len(idxs) > 0:
        # loop over the indexes we are keeping
        for i in idxs.flatten():
            # extract the bounding box coordinates
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])

            # draw a bounding box rectangle and label on the frame
            color = [int(c) for c in COLORS[classIDs[i]]]
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            text = "{}: {:.4f}".format(LABELS[classIDs[i]],confidences[i])
            cv2.putText(frame, text, (x, y - 5),cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            obj = LABELS[classIDs[i]]

            if (obj == "person"):
                human += 1
                accuracy += confidences[i]

    if(human > 0):
        print(" > [PERSON]")
        obj = "person"
        accuracy = accuracy/human
    else:
        print(" > [OTHER]")
        obj = "other"

    print("====>> Writing Image", end="", flush=True)
    cv2.imwrite(filename_image, frame)
    print(" > [DONE]")

    return frame,obj,accuracy,proc_time

def doRecord(filename,frame,camera,id):
    print(f"====>> Recording Object {str(id).zfill(4)}",end="",flush=True)
    # Recording Parameters
    record_time = 0
    height = int(frame.shape[0])
    width = int(frame.shape[1])
    size = (width,height)
    writeVid = cv2.VideoWriter(filename,cv2.VideoWriter_fourcc(*'MJPG'),5, size)

    # Recording Phase
    while(record_time<120):
        frame = CameraHandler.getFrame(camera)
        writeVid.write(frame)
        record_time += 1
    writeVid.release()
    print(" > [DONE]")

def doUpload(base_filename,start_milli,percentage,id,label,accuracy,proc_time):
    global hash,ref_1,ref_2,bucket_1,bucket_2,process
    # Filename
    filename_video = base_filename + "_video.avi"
    filename_image = base_filename + "_image.jpg"

    # Load Video
    print("====>> Loading Video Data",end="",flush=True)
    in_video = open(filename_video, "rb")
    video_byte = in_video.read()
    # Close File Session
    in_video.close()
    print(" > [DONE]")

    # Load Image
    print("====>> Loading Image Data", end="", flush=True)
    in_image = open(filename_image, "rb")
    image_byte = in_image.read()
    # Close File Session
    in_image.close()
    print(" > [DONE]")

    # Blockchain
    print("\n==> Generating Blockchain",end="",flush=True)
    # Generate UUID
    VidIdentifier = Blockchain.getIdentifier()
    ImgIdentifier = Blockchain.getIdentifier()

    # Reset Blockchain Parameters
    data = {}
    telemetry = {}

    # Blockchain Data
    if(hash is None):
        previous = "None"
    else:
        previous = hash

    data.update({"0-0 Data":
        {
            "VidId":Blockchain.encryptMessage(VidIdentifier),
            "ImgId":Blockchain.encryptMessage(ImgIdentifier)
        }})
    telemetry = setTelemetry(telemetry,start_milli,percentage,process,label,accuracy,proc_time)
    data.update({"0-1 Telemetry":telemetry})
    # Block Encapsulation
    block = Blockchain(previous,data)
    hash = Blockchain.getHash(block)
    block.setHash(hash)
    print(" > [DONE]")

    # Blockchain Query and Data Upload
    # Video
    print(f"====>> Uploading Video Data ({len(video_byte)})",end="",flush=True)
    FirebaseHandler.uploadData(bucket_1=bucket_1,bucket_2=bucket_2,byte_data=video_byte,identifier=VidIdentifier)
    print(" > [SUCCESS]")
    # Image
    print(f"====>> Uploading Image Data ({len(image_byte)})", end="", flush=True)
    FirebaseHandler.uploadData(bucket_1=bucket_1,bucket_2=bucket_2, byte_data=image_byte, identifier=ImgIdentifier)
    print(" > [SUCCESS]")
    # Uploading
    print("====>> Uploading Blockchain",end="",flush=True)
    FirebaseHandler.insertData(ref_1=ref_1,ref_2=ref_2,id=id,block=block)
    print(" > [SUCCESS]")
    # Report Telegram
    print("\n==> Sending Notification to Telegram Bot", end="", flush=True)
    botHandler.sendMessage("====>> Object Detected > [{}]".format(label.upper(),"B_"+str(id).zfill(4)),verbose=False)
    botHandler.sendMessage("==> Sending Data to User ... ",verbose=False)
    print("====>> Sending Preview to Telegram Bot", end="", flush=True)
    botHandler.sendPhoto(filename_image,caption="Preview : {} Detected in Block {}".format(label.upper(),"B_"+str(id).zfill(4)))
    print("====>> Sending Video to Telegram Bot", end="", flush=True)
    botHandler.sendVideo(filename_video,filename_image, caption="Video : {} Detected in Block {}".format(label.upper(), "B_" + str(id).zfill(4)))
    print("")

    # Remove Video
    if os.path.isfile(filename_video):
        os.remove(filename_video)

    # Remove Image
    if os.path.isfile(filename_image):
        os.remove(filename_image)
    

def setTelemetry(telemetry,start_milli,percentage,process,label,accuracy,proc_time):
        # Telemetry - Benchmark
    cpu_percent,memory_percent,text_usage,data_usage,cpu_temp = Telemetry.getBenchmarkInfo(process)
    end_milli = current_milli_time()
    time_milli = end_milli - start_milli
    telemetry.update({"1-00 Benchmark":
                    {
                        "1-01 CPU Percent":Blockchain.encryptMessage(cpu_percent),
                        "1-02 Memory Percent":Blockchain.encryptMessage(memory_percent),
                        "1-03 Text Usage":Blockchain.encryptMessage(text_usage),
                        "1-04 Data Usage":Blockchain.encryptMessage(data_usage),
                        "1-05 CPU Temp":Blockchain.encryptMessage(cpu_temp),
                        "1-06 Time Milli":Blockchain.encryptMessage(str(time_milli)),
                        "1-07 Difference":Blockchain.encryptMessage(str(percentage)),
                        "1-08 Mode":Blockchain.encryptMessage(str(label)),
                        "1-09 Confidence":Blockchain.encryptMessage(str(accuracy)),
                        "1-10 YOLO Processing":Blockchain.encryptMessage(str(proc_time))
                    }})

    # Telemetry - Date Time
    day,date,timenow,tzname = Telemetry.getDateTimeInfo()
    telemetry.update({
        "2-00 Datetime":
                    {
                        "2-01 Day":Blockchain.encryptMessage(day),
                        "2-02 Date":Blockchain.encryptMessage(date),
                        "2-03 Time":Blockchain.encryptMessage(timenow),
                        "2-04 Timezone":Blockchain.encryptMessage(tzname)
                    }})
    return telemetry

def current_milli_time():
    return round(time.time() * 1000)

def verifyKeys():
    print("==> Checking Keys",end="",flush=True)
    pubkeypem = os.path.exists("keys/pubkey.pem")
    privkeypem = os.path.exists("keys/privkey.pem")
    if(pubkeypem == True and privkeypem == True):
        print(" > [FOUND]")
        return True
    else:
        print(" > [NOT FOUND]")
        return False

def main():
    global ref_1,ref_2,bucket_1,bucket_2,process,record_lock,counter
    print("Blockchain Human Motion Detection")
    # Verify Keys
    keys  = verifyKeys()
    if(keys == True):
        # Loading Cloud Service
        print("==> Connecting to Firebase",end="",flush=True)
        ref_1,ref_2 = FirebaseHandler.connectDB() # Connect Firebase
        print(" > [CONNECTED]")
        print("==> Connecting to Google Storage",end="",flush=True)
        bucket_1,bucket_2 = FirebaseHandler.connectBucket() # Connect Google Storage
        print(" > [CONNECTED]")
        # Loading Benchmark Service
        print("==> Starting Benchmark Function",end="",flush=True)
        process = Telemetry.getProcess()
        print(" > [STARTED]")
        # Starting Detection
        runDetection()
    else:
        print("==> Detection > [ABORTED]")

if __name__ == '__main__':
        main()
