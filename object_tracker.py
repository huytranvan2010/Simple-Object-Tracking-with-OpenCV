from hammiu import CentroidTracker
import imutils
import argparse
import time
import time 
import cv2
import numpy as np

"""Bài này có thể chọn nhiều face detector như YOLO..."""
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True, help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True, help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.5, help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

# khởi tạo centroid tracker và frame dimensions
ct = CentroidTracker()
(H, W) = (None, None)

# load model
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# load webcam
video = cv2.VideoCapture(0)

# lấy các frames
while True:
    ok, frame = video.read()

    # ko lấy được frame
    if not ok:
        break

    # resize lại chạy cho nhanh
    # frame = imutils.resize(frame, width=500)

    # laays dimensions of frames nếu None
    if H is None and W is None:
        (H, W) = frame.shape[:2]

    # tạo blob từ image - tạo input vào mạng
    blob = cv2.dnn.blobFromImage(frame, 1.0, (W, H), (104.0, 177.0, 123.0))
    # truyền blob vào mạng, nhận được predictions, khởi tạo list chứa bounding boxes
    net.setInput(blob)
    detections = net.forward()
    rects = []

    # Duyệt qua các dự đoán/phát hiện
    for i in range(0, detections.shape[2]):
        # lọc các detection có prob nhỏ, cái nào lớn mới dùng
        if detections[0, 0, i, 2] > args["confidence"]:
            # xác định (x, y) của bounding box rồi cập nhật vào rects
            box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
            rects.append(box.astype("int"))     # chuyển về int do pixel

            # vẽ bounding box quanh object để có thể biểu diễn chúng
            (startX, startY, endX, endY) = box.astype("int")
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
    
    # update centroid tracker bằng các bounding boxes vừa tính
    objects = ct.update(rects)

    # duyệt qua các tracked objects
    for (objectID, centroid) in objects.items():
        # vẽ ID của object và centroid lên frame
        text = "ID {}".format(objectID)
        cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break 

cv2.destroyAllWindows()
video.release()


            
    