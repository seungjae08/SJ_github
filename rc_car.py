
import socket
import cv2
import numpy as np
import math

def angle(dx, dy):
    return math.atan2(dy, dx) * 180 / math.pi
def region_of_interest(img, vertices, color3=(255, 255, 255), color1=255):

    mask = np.zeros_like(img)

    if len(img.shape) > 2:
        color = color3
    else:
        color = color1


    cv2.fillPoly(mask, vertices, color)


    ROI_image = cv2.bitwise_and(img, mask)
    return ROI_image
class StreamingServer(object):
    def __init__(self):
        #self.restUrl = 'http://192.168.0.6:8080/control'
        self.restUrl = 'http://192.168.0.8:5002/messages'
        self.server_socket = socket.socket()
        self.server_socket.bind(('192.168.0.2', 8001))

        self.server_socket.listen(1)
        self.conn, self.client_address = self.server_socket.accept()
        self.connection = self.conn.makefile('rb')
        self.server_socket.setblocking(False)
        self.streamingAndCollectData()



    def streamingAndCollectData(self):
        # collect images for training
        print('Start collecting images...')

        try:
            q=[0,0,0]
            print("Connection from: ", self.client_address)
            print("Streaming...")
            print("Press 'Q' to exit")
            c=None
            stream_bytes = b''
            frame = 1
            while True:

                stream_bytes += self.connection.read(1024)
                first = stream_bytes.find(b'\xff\xd8')
                last = stream_bytes.find(b'\xff\xd9')
                self.conn.sendall(b'WA')
                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last + 2]
                    stream_bytes = stream_bytes[last + 2:]
                    image = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), 0)
                    height,width = image.shape[:2]
                    mark = np.copy(image)
                    blue_threshold=75
                    green_threshold =75
                    red_threshold = 75
                    bgr_threshold = [blue_threshold,green_threshold,red_threshold]

                    thresholds = (image[:, :, 0] > bgr_threshold[0]) \
                                 | (image[:, :, 1] > bgr_threshold[1]) \
                                 | (image[:, :, 2] > bgr_threshold[2])
                    mark[thresholds] = [255, 255, 255]
                    img = cv2.cvtColor(mark, cv2.COLOR_BGR2GRAY)
                    img = cv2.GaussianBlur(mark, (3,3),0)
                    dst = cv2.Canny(img, 70, 210)
                    vertices = np.array([[(50, height), (width / 2 - 45, height / 2 + 60),
                                          (width / 2 + 45, height / 2 + 60), (width - 50, height)]], dtype=np.int32)

                    ROI_img = region_of_interest(dst,vertices)
                    row, col = mark.shape[:2]
                    cimg = mark.copy()  # numpy function
                    lines = cv2.HoughLinesP(ROI_img, 1, math.pi / 180.0, 30, np.array([]), 10, 20)
                    #circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 10, np.array([]), 100, 30, 1, 30)

                    if lines is not None:
                        a, b, c = lines.shape
                        (d, e) = (row / 2, row / 2)
                        (f, g) = (-1, -1)

                        for i in range(a):
                            (x1, y1, x2, y2) = (lines[i][0][0], lines[i][0][1], lines[i][0][2], lines[i][0][3])

                            if max(lines[i][0][1], lines[i][0][3]) > row / 2 and min(x1, x2) < col / 2 and angle(
                                    x2 - x1, y2 - y1) < 0:
                                d = max(y1, y2)
                                f = i

                            if max(lines[i][0][1], lines[i][0][3]) > row / 2 and min(x1, x2) > col / 2 and angle(
                                    x2 - x1, y2 - y1) > 0:
                                d = max(y1, y2)
                                g = i
                            if f != -1 and g != -1 and q[0]==0:
                                q=[1,0,0]
                                print("straight")
                                payload = dict(data='w')
                                response = requests.post(self.restUrl, params=payload)
                                print(response, payload, 'sent to server.')



                            if g != -1 and f == -1 and q[1]==0:
                                q=[0,1,0]
                                print("left")
                                payload = dict(data='a')
                                response = requests.post(self.restUrl, params=payload)
                                print(response, payload, 'sent to server.')

                            if f != -1 and g == -1 and q[2]==0:
                                q=[0,0,1]
                                print("right")
                                payload = dict(data='d')
                                response = requests.post(self.restUrl, params=payload)
                                print(response, payload, 'sent to server.')

                        if f != -1:
                            (x1, y1, x2, y2) = (lines[f][0][0], lines[f][0][1], lines[f][0][2], lines[f][0][3])
                            #print("righy side angle is", angle(y2 - y1, x2 - x1))
                            cv2.line(mark, (x1, y1), (x2, y2), (0, 0, 255), 3, cv2.LINE_AA)

                        if g != -1:
                            (x1, y1, x2, y2) = (lines[g][0][0], lines[g][0][1], lines[g][0][2], lines[g][0][3])
                            #print("left side angle is", angle(y2 - y1, x2 - x1))
                            cv2.line(mark, (x1, y1), (x2, y2), (0, 0, 255), 3, cv2.LINE_AA)

                    cv2.imshow('image1',image)
                    cv2.imshow('image', mark)

                    if cv2.waitKey(1) == 27:
                        exit(0)

        finally:
            self.connection.close()
            self.server_socket.close()

if __name__ == '__main__':
    StreamingServer()
