from scipy.spatial import distance as dist
from collections import OrderedDict     # như dictionary bt nhưng có lưu thứ tự chèn vào
import numpy as np

class CentroidTracker():
    def __init__(self, maxDisappeared=50):  # 50 khung hình ko
        """ Khởi tạo CentroidTracker class với tham số truyền vào là maxDisappeared """
        # khởi tạo unique object ID tiếp theo cùng với 2 dictionaries để theo dõi mapping
        # của object ID đến centroid của nó và số frames liên tục nó có để có thể đánh dấu là "disappear"
        self.nextObjectID = 0
        self.objetcs = OrderedDict()    # key là ID, value là centroid
        self.disappeared = OrderedDict()    # key là ID, value là số khung hình ko khớp được

        # lưu số lượng max frames liên tục để dùng nếu objetc không xuất hiện lại 
        # thì cho nó "disappear", deregrister khỏi theo dõi
        self.maxDisappeared = maxDisappeared

    def register(self, centroid):
        """ Add new objects to the tracker """
        # ghi nhận object thì sử dụng ID tiếp theo để lưu centroid tương ứng
        self.objetcs[self.nextObjectID] = centroid
        self.disappeared[self.nextObjectID] = 0     # số lần biến mất cho object hiện tại = 0, vì mới ghi nhận
        self.nextObjectID += 1      # đã ghi nhận được 1 vật thể thì tăng lên 1

    def deregister(self, objectID):
        """ Xóa object nếu không được khớp sau N khung hình liên tiếp, xóa theo objectID thôi """
        # để deregrister object ID chúng ta sẽ xóa object ID khỏi các dictionaries
        del self.objetcs[objectID]
        del self.disappeared[objectID]

    def update(self, rects):    # bounding boxes từ các object detector
        """ Thực hiện tracking """
        # Kiêm tra nếu ko có detections, tăng số frame disappear và kiểm tra đạt Max chưa thì loại ko theo dõi nữa
        if len(rects) == 0:
            # duyệt qua các objets bị theo dõi có sẵn và tăng số lần biến mất của chúng (khung hình ko có)
            for objetcID in list(self.disappeared.keys()):
                self.disappeared[objetcID] += 1

                # nếu số lần biến mất đạt max thì loại bỏ khỏi danh sách theo dõi deregrister
                if self.disappeared[objetcID] > self.maxDisappeared:
                    self.deregister(objetcID)   # xóa cả trong objetcs và disappeared

            # ko có centroids nào được thêm vào hoặc tracking
            return self.objetcs
            
        # khởi tạo array các input centroids cho FRAME HIỆN TẠI
        # vị một bounding box có 1 centroid với 2 tọa độ
        inputCentroids = np.zeros((len(rects), 2), dtype='int')     

        # duyệt qua các bounding boxes để lấy centroids, lưu vào inputCentroids
        for (i, (startX, startY, endX, endY)) in enumerate(rects):
            cX = int((startX + endX) / 2)
            cY = int((startY + endY) / 2)
            inputCentroids[i] = (cX, cY)
        
        # Nếu chưa có vật thể nào được theo dõi thì sẽ lấy centroids mới và ghi nhận
        if len(self.objetcs) == 0:
            for i in range(0, len(inputCentroids)):
                self.register(inputCentroids[i])
        
        # còn không chúng ta sẽ update bất kì vật thể đã được theo dõi nếu thỏa mãn minimum Euclidean distance
        else:
            # lấy ID và centroids của object đang được theo dõi
            objectIDs = list(self.objetcs.keys())
            objectCentroids = list(self.objetcs.values())

            # tính toán distance giữa các object centroids (đang được theo dõi) và
            # input centroids (khung hình hiện tại), từng cặp một
            # Compute distance between each pair of the two collections of inputs.
            ''' output có shape (# objetc centroids, # input centroids), for i, j dist(A[i], B[j]) '''
            D = dist.cdist(np.array(objectCentroids), inputCentroids)   

            # để xác định được matching (sự khớp) chúng ta cần tìm giá trị nhỏ nhất 
            # cho mỗi hàng (mỗi hàng là distance của centroid đã có với tất cả input centroid)
            # sắp xếp các indexes của các hàng dựa trên giá trị các giá trị min
            """ Nên nhớ rows chỉ chứa các chỉ số của object đã tồn tại do đánh số từ 0 """
            rows = D.min(axis=1).argsort() 

            # thực hiện tương tự với cột bằng cách tìm giá trị min trong mỗi cột sau đó sắp xếp sử
            # dụng các row index list trước đó
            # cols = D[rows].argmin(axis=1)
            cols = D.argmin(axis=1)[rows]

            usedRows = set()    # giống list như chỉ chứa đựa unique value, dùng {}
            usedCols = set()

            # duyệt qua các combination của (row, column) index tuple
            """ Ở đây đã sắp xếp rồi nên sẽ xử lý các cặp có distance nhỏ nhất đã """
            for (row, col) in zip(rows, cols):
                # nếu đã kiểm tra hàng hay cột nào thì bỏ qua
                if row in usedRows or col in usedCols:
                    continue

                # còn ko thì lấy object ID cho hàng đang duyệt, set its new centroid, và
                # reset the disappeared counter
                objectID = objectIDs[row]
                self.objetcs[objectID] = inputCentroids[col]
                self.disappeared[objectID] = 0

                # đã kiểm tra rồi thì add vào set đã dùng
                usedRows.add(row)
                usedCols.add(col)

            # tính cả row và column index chúng ta chưa kiểm tra   
            # A, B là 2 sets, A.difference(B) - các phần tử chỉ có trong A mà ko có trong B
            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            unusedCols = set(range(0, D.shape[1])).difference(usedCols)

            """ Trường hợp số object centroids >= số input centroids, nghĩa là có vật thể biến mất khỏi frame """
            if D.shape[0] >= D.shape[1]:
                # duyệt qua các unusedRows indexes
                for row in unusedRows:
                    # laays object ID for the corresponding row
                    # index and increment the disappeared counter
                    objectID = objectIDs[row]
                    self.disappeared[objectID] += 1

                    # kiểm tra nếu số frames liên tiếp lớn hơn max thì deregister
                    if self.disappeared[objectID] > self.maxDisappeared:
                        self.deregister(objectID)

            # còn ko sẽ có new object D.shape[0] < D.shape[1]
            # nên nhớ ko được so sánh len(rows) và len(cols) nó chúng luôn bằng nhau và = len(rows)
            else: 
                for col in unusedCols:
                    self.register(inputCentroids[col])
        
        return self.objetcs




    