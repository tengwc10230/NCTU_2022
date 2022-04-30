import cv2 as cv
from numpy import *

def mouse_action(event, x, y, flags, replace_coordinate_array):
    cv.imshow('collect coordinate', img_dest_copy)
    if event == cv.EVENT_LBUTTONUP:
        cv.circle(img_dest_copy, (x, y), 2, (0, 255, 255), -1)

        print(f'{x}, {y}')
        replace_coordinate_array.append([x, y])


def findHomographyMatrix(u, v):
    N = u.shape[0]
    if v.shape[0] is not N:
        print('u and v should have the same size')
        return None
    if N < 4:
        print('At least 4 points should be given')

    A = array([[u[0][0], u[0][1], 1, 0, 0, 0, -1 * u[0][0] * v[0][0], -1 * u[0][1] * v[0][0]],
               [0, 0, 0, u[0][0], u[0][1], 1, -1 * u[0][0] * v[0][1], -1 * u[0][1] * v[0][1]],
               [u[1][0], u[1][1], 1, 0, 0, 0, -1 * u[1][0] * v[1][0], -1 * u[1][1] * v[1][0]],
               [0, 0, 0, u[1][0], u[1][1], 1, -1 * u[1][0] * v[1][1], -1 * u[1][1] * v[1][1]],
               [u[2][0], u[2][1], 1, 0, 0, 0, -1 * u[2][0] * v[2][0], -1 * u[2][1] * v[2][0]],
               [0, 0, 0, u[2][0], u[2][1], 1, -1 * u[2][0] * v[2][1], -1 * u[2][1] * v[2][1]],
               [u[3][0], u[3][1], 1, 0, 0, 0, -1 * u[3][0] * v[3][0], -1 * u[3][1] * v[3][0]],
               [0, 0, 0, u[3][0], u[3][1], 1, -1 * u[3][0] * v[3][1], -1 * u[3][1] * v[3][1]]
            ])

    b = array([[v[0][0]],
               [v[0][1]],
               [v[1][0]],
               [v[1][1]],
               [v[2][0]],
               [v[2][1]],
               [v[3][0]],
               [v[3][1]]
            ])

    tmp = dot(linalg.inv(A), b)
    H = array([[tmp[0][0], tmp[1][0], tmp[2][0]],
                  [tmp[3][0], tmp[4][0], tmp[5][0]],
                  [tmp[6][0], tmp[7][0], 1]
                 ])

    return H


if __name__ == '__main__':
    img_src = cv.imread("laugh.jpg", cv.IMREAD_COLOR)
    h, w, c = img_src.shape
    img_src_coordinate = array([[x, y] for x in (0, w - 1) for y in (0, h - 1)])
    print(img_src_coordinate)

    print("===========================")

    img_dest = cv.imread("background.png", cv.IMREAD_COLOR)
    img_dest_copy = tile(img_dest, 1)

    replace_coordinate = []
    cv.namedWindow('collect coordinate')
    cv.setMouseCallback('collect coordinate', mouse_action, replace_coordinate)
    while True:
        if cv.waitKey(20) == 27:
            break

    print(replace_coordinate)

    replace_coordinate = array(replace_coordinate)
    # matrix, _ = cv.findHomography(img_src_coordinate, replace_coordinate, 0)
    matrix = findHomographyMatrix(img_src_coordinate, replace_coordinate)
    # print(f'matrix: {matrix}  tmp_matrix: {tmp_matrix}')
    perspective_img = cv.warpPerspective(img_src, matrix, (img_dest.shape[1], img_dest.shape[0]))
    # cv.imshow('img', perspective_img)

    retval, threshold_img = cv.threshold(perspective_img, 0, 255, cv.THRESH_BINARY)
    cv.copyTo(src=threshold_img, mask=tile(threshold_img, 1), dst=img_dest)
    cv.copyTo(src=perspective_img, mask=tile(perspective_img, 1), dst=img_dest)
    cv.imshow('result', img_dest)
    cv.imwrite('result.jpg', img_dest)
    cv.waitKey()
    cv.destroyAllWindows()