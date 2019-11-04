import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from skimage import data, io
from skimage.feature import canny
from skimage.transform import probabilistic_hough_line

def houghOnImg(arg1):      
    image = np.zeros((320, 240))
    image = io.imread(arg1, as_gray=True)
    im2 = canny(image, sigma=2)
    hugh = probabilistic_hough_line(im2)

    fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, figsize=(8, 3),
                                        sharex=True, sharey=True)
    ax1.imshow(image, cmap=plt.cm.gray)
    ax1.axis('off')
    ax1.set_title('noisy image', fontsize=20)

    ax2.imshow(im2, cmap=plt.cm.gray)
    ax2.axis('off')
    ax2.set_title('Canny filter, $\sigma=1$', fontsize=20)

    ax3.imshow(im2 * 0)
    print(len(hugh))
    for line in hugh:
        p0, p1 = line
        print(p0,p1)
        ax3.plot((p0[0], p1[0]), (p0[1], p1[1]))
    ax3.set_xlim((0, image.shape[1]))
    ax3.set_ylim((image.shape[0], 0))
    ax3.axis("off")
    ax3.set_title('Probabilistic Hough')


    fig.tight_layout()
    plt.show()

houghOnImg("images/0.jpg")