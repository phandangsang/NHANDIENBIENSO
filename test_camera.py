import cv2

cap = cv2.VideoCapture(0)

print("Opened:", cap.isOpened())

while True:
    ret, frame = cap.read()

    if ret:
        cv2.imshow("Camera Test", frame)

    key = cv2.waitKey(1)

    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()