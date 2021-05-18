# Simple-Object-Tracking-with-OpenCV

Object tracking là quá trình bao gồm:
* Lấy bộ các object detections (ví dụ tọa độ của bộ bounding boxes)
* Tạo ID duy nhất cho mỗi detection
* Tracking theo các vật thể khi nó di chuyển, duy trì ID đó

Object tracking áp dụng ID duy nhất giúp chúng ta có thể đém vật thể trong video.

Thuật toán object tracking lý tưởng có các ýếu tố sau:
* Chỉ cần thực hiện object detection một lần
* Có thể xử lý được các vật thể được theo dõi "biến mất" hoặc di chuyển ra ngoài giới hạn video frame
* Vẫn có thể theo dõi được các đối tượng "biến mất" giữa các khung hình
* Be robust to occlusion

Trong bài này chúng ta sẽ thực hiện simple object tracking algorithm - centroid tracking. Algorithm này dưa trên Euclidean distance giữa:
- Existing object centroids (các tâm vật thể đã có - đã được theo dõi)
- New object centroids (các tâm vật thể mới trong các khung hình tiếp theo)

# Centroid tracking algorithm
Centroid tracking algorithm là quá trình nhiều bước (multi-step). 
* **Bước 1:** Accept bounding box coordinates and compute centroids: Lấy tọa độ của bounding boxes từ object detector sau đó sử dụng chúng để xác định centroids. Object detector có thể là HOG + Linear SVM, SSDs, Faster R-CNN... Do đây là các bounding box được tạo đầu tiên nên ta sẽ gán cho chúng ID duy nhất.
* **Bước 2:** Xác định Euclidean distance between new bounding boxes and existing objects

Cho các frame tiếp theo trong video chúng ta thwucj hiện **Bước 1** để xác định centroids. Tuy nhiên thay vì gán ID duy nhất mới cho các vật thể phát hiện được (không còn là object tracking) chúng ta cần xác định nếu có sự liên quan giữa `new object centroid` và `old object centroid` không. Để thực hiện điều này chúng ta đi tính Euclidean distance giữa các cặp existing object centroids và input object centroids.

* **Bước 3:** Updata (x, y) cooordinates of existing objects
