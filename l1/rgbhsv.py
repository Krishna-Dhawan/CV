import cv2
import matplotlib.pyplot as plt

img_bgr = cv2.imread("datasets/sipi/misc/4.2.07.tiff")
img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

R, G, B = cv2.split(img_rgb)
H, S, V = cv2.split(img_hsv)

fig, axes = plt.subplots(2, 4, figsize=(16, 8))

axes[0, 0].imshow(img_rgb)
axes[0, 0].set_title("Original (RGB)")

axes[0, 1].imshow(R, cmap="Reds")
axes[0, 1].set_title("Red Channel")

axes[0, 2].imshow(G, cmap="Greens")
axes[0, 2].set_title("Green Channel")

axes[0, 3].imshow(B, cmap="Blues")
axes[0, 3].set_title("Blue Channel")

axes[1, 0].imshow(img_hsv)
axes[1, 0].set_title("Original (as HSV array)")

axes[1, 1].imshow(H, cmap="hsv")
axes[1, 1].set_title("Hue")

axes[1, 2].imshow(S, cmap="gray")
axes[1, 2].set_title("Saturation")

axes[1, 3].imshow(V, cmap="gray")
axes[1, 3].set_title("Value")

for ax in axes.ravel():
    ax.axis("off")

plt.tight_layout()
plt.show()