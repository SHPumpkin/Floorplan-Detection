import cv2


def door_detection(image, erosion_size=3, scale_factor=1.24, min_neighbors=1):
    door_cascade = cv2.CascadeClassifier("cascade_600_1500.xml")
    image_copy = image.copy()
    element = cv2.getStructuringElement(cv2.MORPH_RECT, (int(erosion_size), int(erosion_size)))
    prepared_img = cv2.erode(image_copy, element)
    doors = door_cascade.detectMultiScale(prepared_img, scale_factor, int(min_neighbors))

    for (x, y, w, h) in doors:
        cv2.rectangle(image_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # cv2.imshow("doors", image_copy)
    # cv2.imwrite("doors.png", image_copy)
    # cv2.waitKey(0)
    return doors
