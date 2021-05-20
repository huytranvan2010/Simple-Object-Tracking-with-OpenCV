import numpy as np

D = np.array([[1, 3, 2, 4], [4.6, 8, 4, 3], [7.2, 2.3, 1.5, 6]])

""" Nếu existing centroids = 4, current centroids = 3, lúc này sẽ có sự lặp lại của cột có nghĩa là dùng chung current centroid"""
""" Nói chung len(rows) = len(cols) = số existing centroids, cần xem có sự trùng lắp"""
# D = np.array([[1, 3, 2], [4.6, 4, 3], [7.2, 2.3, 1.5], [0.8, 0.4, 1.3]])

# lấy giá trị min theo các hàng rồi sắp xếp chúng tăng dần
# sẽ nhận được list các index của các hàng mà có giá trị min tăng dần
rows = D.min(axis=1).argsort()

# Sau đó sẽ xác định được các chỉ số cột tương ứng với chỉ số hàng đã được sắp xếp có giá trị nhỏ nhất
cols = D.argmin(axis=1)[rows]

print(rows)
print(cols)
# print(D[0, 0], D[2,2], D[1, 3])

"""
    Bên trên hơi khó hiểu, mình làm theo cái này dễ hiểu hơn.
    1. Lấy được index của các hàng mà trong đó min của các hàng được sắp xếp tăng dần
    2. Sắp xếp lại ma trận khoảng cách theo thứ tự các hàng bên trên
    3. Lấy index của colum tương ứng với các hàng để có giá trị min nhất trong hàng đó

    Cuối cùng nhận lại được 2 list là rows và cols. (i, j) thuộc (rows, cols) sẽ chỉ
    chỉ số tương ứng trong ma trân trận khoảng cách mà giá trị của nó trong hàng i là min.
    Các giá trị này được sắp xếp tăng dần.
"""
rows = D.min(axis=1).argsort()

D_new = D[rows]   # nhớ rows đang ở dạng list rồi

cols = D_new.argmin(axis=1)

print(rows)
print(cols)

for (row, col) in zip(rows, cols):
    print(row, col)

"""
    Kết quả trả về rows = [0, 2, 1], cols = [0, 2, 3]
    Do đó D[0, 0] = 1 < D[2, 2] = 1.5 < D[1, 3] = 3
    nên nhớ D[0, 0] = 1 là min của hàng 0
    D[2, 2] = 1.5 là min của hàng 2
    D[1, 3] = 3 là min của hàng 3

    Mình lấy min của từng hàng, sắp xếp min đó theo thứ tự tăng dần, lúc đó sẽ dần lấy được các object match
    với nhau, cứ như vậy cho đến số rows - chính là số existing objects
"""
