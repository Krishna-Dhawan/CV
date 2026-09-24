import cv2

img = cv2.imread("datasets/sipi/misc/4.2.07.tiff")

if img is None:
    raise FileNotFoundError("Could not read the image — check the path.")

# # 1. Auto-size window: window shrinks/grows to exactly fit the image, cannot be resized by the user
# cv2.namedWindow("AutoSize Window", cv2.WINDOW_AUTOSIZE)
# cv2.imshow("AutoSize Window", img)


# 2. Resizable window: user can drag to resize; image is scaled to fit
cv2.namedWindow("Resizable Window", cv2.WINDOW_NORMAL)
cv2.imshow("Resizable Window", img)

# # 3. Fixed-size window: force a specific window size regardless of image size
# cv2.namedWindow("Fixed Size Window", cv2.WINDOW_NORMAL)
# cv2.resizeWindow("Fixed Size Window", 400, 300)
# cv2.imshow("Fixed Size Window", img)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

angle = 45  # hardcoded rotation angle, in degrees (counter-clockwise)

(h, w) = img.shape[:2]
(cX, cY) = (w // 2, h // 2)   # rotate about the image center

M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)  # 1.0 = no additional scaling

# ---- Clipped rotation: same output dimensions as input ----
rotated_clipped = cv2.warpAffine(img, M, (w, h))

# ---- Unclipped rotation: expand canvas to fit the whole rotated image ----
cos = abs(M[0, 0])
sin = abs(M[0, 1])

new_w = int((h * sin) + (w * cos))
new_h = int((h * cos) + (w * sin))

# Shift the rotation matrix so the image is centered in the new, larger canvas
M[0, 2] += (new_w / 2) - cX
M[1, 2] += (new_h / 2) - cY

rotated_unclipped = cv2.warpAffine(img, M, (new_w, new_h))

cv2.imshow("Clipped Rotation", rotated_clipped)
cv2.imshow("Unclipped Rotation", rotated_unclipped)
cv2.waitKey(0)
cv2.destroyAllWindows()