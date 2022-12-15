# Firebase Section
from FirebaseHandler import FirebaseHandler
# Telegram Handler
from TelegramHandler import *
# Blockchain Section
from Blockchain import Blockchain
# Additional Section
import os
import time
import numpy as np
import cv2
import imutils

# Hyperparameter
ref_1 = None
ref_2 = None
ref_3 = None
bucket_1 = None
bucket_2 = None
last_id = 1

botHandler = TelegramHandler()

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

def dataFetch():
    db_1 = ref_1.get()
    db_2 = ref_2.get()
    print("==> Checking Database for Marking",end="",flush=True)

    if (db_1 is not None and db_2 is not None):
        print(" > [FOUND]")
        # Iterate Machine
        for machine in db_1.keys():
            blocks = ref_1.child(machine).get()
            # Iterate Block Data
            for block in blocks.keys():
                if(int(block[2:])>=last_id):
                    ImageFile = None
                    VideoFile = None
                    block_data = ref_1.child(machine).child(block).get()
                    video_id = block_data['02 Data']['0-0 Data']['VidId']
                    image_id = block_data['02 Data']['0-0 Data']['ImgId']
                    # Clear File
                    if os.path.isfile(f"Records/{block}_vid.avi"):
                        os.remove(f"Records/{block}_vid.avi")
                    # Clear File
                    if os.path.isfile(f"Records/{block}_vid_marked.avi"):
                        os.remove(f"Records/{block}_vid_marked.avi")
                    if os.path.isfile(f"Records/{block}_img.jpg"):
                        os.remove(f"Records/{block}_img.jpg")
                    # Fetch Data Try Catch
                    while True:
                        print(f"==> Downloading Block {block}'s Data", end="", flush=True)
                        botHandler.sendMessage(f"==> Downloading Block {block}'s Data",verbose=False)
                        try:
                            image_data, statusimg = FirebaseHandler.downloadData(bucket_1, bucket_2,
                                                                                 Blockchain.decryptMessage(str(image_id)))
                            video_data, statusvid = FirebaseHandler.downloadData(bucket_1, bucket_2,
                                                                                 Blockchain.decryptMessage(str(video_id)))
                            print(" > [SUCCESS]")
                            botHandler.sendMessage(f"====>> Success",verbose=False)
                            if(statusvid == True and statusimg == True):
                                break
                            else:
                                print(" > [RETRYING]")
                        except Exception as e:
                            print(" > [LIMIT REACHED]")
                            print(e)
                            botHandler.sendMessage(f"====>> Limit Reached",verbose=False)
                            time.sleep(3600) # 24 Hr
                    # Write to File
                    print(f"==> Writing {block}'s Data to File", end="", flush=True)
                    botHandler.sendMessage(f"==> Writing {block}'s Data to File",verbose=False)
                    ImageFile = open(f"Records/{block}_img.jpg","wb")
                    ImageFile.write(image_data)
                    ImageFile.close()
                    VideoFile = open(f"Records/{block}_vid.avi","wb")
                    VideoFile.write(video_data)
                    VideoFile.close()
                    print(" > [SUCCESS]")
                    botHandler.sendMessage(f"====>> Success",verbose=False)

                    # Mark Video for Object Detection
                    print(f"==> Marking {block}'s Video", end="", flush=True)
                    botHandler.sendMessage(f"==> Marking {block}'s Video", verbose=False)
                    label,accuracy = markVideo(f"Records/{block}_vid.avi",block)
                    print(" > [SUCCESS]")
                    botHandler.sendMessage(f"====>> Success", verbose=False)
                    # Remove Existing
                    print(f"==> Removing Unmarked {block}'s Video", end="", flush=True)
                    botHandler.sendMessage(f"==> Removing Unmarked {block}'s Video", verbose=False)
                    if os.path.isfile(f"Records/{block}_vid.avi"):
                        os.remove(f"Records/{block}_vid.avi")
                    print(" > [SUCCESS]")
                    botHandler.sendMessage(f"====>> Success", verbose=False)
                    print(f"==> Uploading Benchmark", end="", flush=True)
                    botHandler.sendMessage(f"==> Uploading Benchmark", verbose=False)
                    doUpload(block,label,accuracy,ref_3)
                    print(" > [SUCCESS]")
                    botHandler.sendMessage(f"====>> Success", verbose=False)

    else:
        print(" > [NOT FOUND]")

def markVideo(filename_video,block):
    obj = None
    human = 0
    accuracy = 0
    # Load YOLO COCO
    labelsPath = os.path.sep.join(["yolo-coco", "coco.names"])
    LABELS = open(labelsPath).read().strip().split("\n")

    # initialize a list of colors to represent each possible class label
    np.random.seed(42)
    COLORS = np.random.randint(0, 255, size=(len(LABELS), 3), dtype="uint8")

    # derive the paths to the YOLO weights and model configuration
    weightsPath = os.path.sep.join(["yolo-coco", "yolov3.weights"])
    configPath = os.path.sep.join(["yolo-coco", "yolov3.cfg"])

    # load our YOLO object detector trained on COCO dataset (80 classes)
    # and determine only the *output* layer names that we need from YOLO
    net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
    ln = net.getLayerNames()
    ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()]

    # Load Video
    vs = cv2.VideoCapture(filename_video)
    writer = None
    (W, H) = (None, None)

    # try to determine the total number of frames in the video file
    try:
        prop = cv2.cv.CV_CAP_PROP_FRAME_COUNT if imutils.is_cv2() \
            else cv2.CAP_PROP_FRAME_COUNT
        total = int(vs.get(prop))

    # an error occurred while trying to determine the total
    # number of frames in the video file
    except:
        total = -1

    # loop over frames from the video file stream
    while True:
        # read the next frame from the file
        (grabbed, frame) = vs.read()

        # if the frame was not grabbed, then we have reached the end
        # of the stream
        if not grabbed:
            break

        # if the frame dimensions are empty, grab them
        if W is None or H is None:
            (H, W) = frame.shape[:2]

        # construct a blob from the input frame and then perform a forward
        # pass of the YOLO object detector, giving us our bounding boxes
        # and associated probabilities
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),
                                     swapRB=True, crop=False)
        net.setInput(blob)
        layerOutputs = net.forward(ln)

        # initialize our lists of detected bounding boxes, confidences,
        # and class IDs, respectively
        boxes = []
        confidences = []
        classIDs = []

        # loop over each of the layer outputs
        for output in layerOutputs:
            # loop over each of the detections
            for detection in output:
                # extract the class ID and confidence (i.e., probability)
                # of the current object detection
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]

                # filter out weak predictions by ensuring the detected
                # probability is greater than the minimum probability
                if confidence > 0.5:
                    # scale the bounding box coordinates back relative to
                    # the size of the image, keeping in mind that YOLO
                    # actually returns the center (x, y)-coordinates of
                    # the bounding box followed by the boxes' width and
                    # height
                    box = detection[0:4] * np.array([W, H, W, H])
                    (centerX, centerY, width, height) = box.astype("int")

                    # use the center (x, y)-coordinates to derive the top
                    # and and left corner of the bounding box
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))

                    # update our list of bounding box coordinates,
                    # confidences, and class IDs
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    classIDs.append(classID)

        # apply non-maxima suppression to suppress weak, overlapping
        # bounding boxes
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.5,0.3)

        # ensure at least one detection exists
        if len(idxs) > 0:
            # loop over the indexes we are keeping
            for i in idxs.flatten():
                # extract the bounding box coordinates
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])

                obj = LABELS[classIDs[i]]

                if (obj == "person"):
                    human += 1
                    accuracy = confidences[i]

                    # draw a bounding box rectangle and label on the frame
                    color = [int(c) for c in COLORS[classIDs[i]]]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    text = "{}: {:.4f}".format(LABELS[classIDs[i]],confidences[i])
                    cv2.putText(frame, text, (x, y - 5),cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            if (human > 0):
                obj = "person"
            else:
                obj = "other"

        # check if the video writer is None
        if writer is None:
            # initialize our video writer
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            writer = cv2.VideoWriter(f"Records/{block}_vid_marked.avi", fourcc, 30,
                                     (frame.shape[1], frame.shape[0]), True)

        # write the output frame to disk
        writer.write(frame)

    # release the file pointers
    writer.release()
    vs.release()
    return obj,accuracy

def doUpload(block,label,accuracy,ref_3):
    data = {}
    data.update({"Label": label,"Accuracy": accuracy})
    ref_3.child(block).set(data)

def main():
    global ref_1,ref_2,ref_3,bucket_1,bucket_2
    print("=> Video Marking Service")
    # Verify Keys
    keys = verifyKeys()
    if (keys == True):
        # Loading Cloud Service
        print("==> Connecting to Firebase", end="", flush=True)
        ref_1,ref_2 = FirebaseHandler.connectDB()  # Connect Firebase
        print(" > [CONNECTED]")
        print("==> Connecting to Benchmark Database", end="", flush=True)
        ref_3 = FirebaseHandler.connectThirdDB()  # Connect Firebase
        print(" > [CONNECTED]")
        print("==> Connecting to Google Storage", end="", flush=True)
        bucket_1,bucket_2 = FirebaseHandler.connectBucket()  # Connect Google Storage
        print(" > [CONNECTED]")
        dataFetch()
    else:
        print("==> Detection > [ABORTED]")

if __name__ == '__main__':
    main()
