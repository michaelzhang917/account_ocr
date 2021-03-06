import cv2
import pytesseract
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import argparse


def OCRTextLine(img, baseHeight=100, blurSize=5, threshold=180, lang='eng', boxes=False, showPlots=False):
    height, width = img.shape[:2]
    scale = baseHeight/height
    newHeight = int(baseHeight)
    newWidth = int(scale*width)
    imgres = cv2.resize(img,(newWidth, newHeight), interpolation=cv2.INTER_LINEAR)
    gray = cv2.cvtColor(imgres, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(blurSize,blurSize),0)
    binary_output = np.zeros_like(blur)
    binary_output[blur < threshold] = 1
    img = Image.fromarray(np.uint8((binary_output)))
    output = pytesseract.image_to_string(img, lang, boxes, config="-psm 7")
    if showPlots:
        plt.figure()
        plt.subplot(141)
        plt.imshow(imgres)
        plt.title('original')
        plt.axis('off')
        plt.subplot(142)
        plt.imshow(gray, cmap='gray')
        plt.title('gray')
        plt.axis('off')
        plt.subplot(143)
        plt.imshow(blur, cmap='gray')
        plt.title('blur')
        plt.axis('off')
        plt.subplot(144)
        plt.imshow(binary_output, cmap='gray')
        plt.title('binary')
        plt.axis('off')
    return output


def histConstruct(img, axis=1, blurSize=9, threshold=180, showPlot=False):
    height, width = img.shape[:2]
    img = cv2.resize(img,(width, height), interpolation = cv2.INTER_NEAREST)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(blurSize, blurSize),0)
    binary_output = np.zeros_like(blur)
    binary_output[blur < threshold] = 1
    hist = np.sum(binary_output, axis)
    if showPlot:
        plt.figure()
        plt.plot(hist)
    return hist


def findTextLine(hist):
    listOfLines = list()
    start = -1
    for i in range(len(hist) - 1):
        if hist[i] == 0 and hist[i+1] > 0:
            start = i
        if hist[i] > 0 and hist[i+1] == 0 and start != -1:
            end = i+1
            listOfLines.append((start, end))
    return listOfLines


def cropLines(img, lineloc, offset=4):
    return img[max(lineloc[0] - offset, 0) : lineloc[1] + offset, :]


def pipeline(filename, top_left = (0,0), bottom_right = None):
    img = cv2.imread(filename)
    if bottom_right is None:
        bottom_right = (img.shape[0], img.shape[1])
    img = img[top_left[0]:bottom_right[0], top_left[1]:bottom_right[1]]
    hist = histConstruct(img)
    linesLocation = findTextLine(hist)
    listOfresults = list()
    for lineloc in linesLocation:
        listOfresults.append(OCRTextLine(cropLines(img, lineloc)))
    return linesLocation, listOfresults


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='OCR text')
    parser.add_argument(
        'filename',
        type=str,
        help='The image file for OCR'
    )
    parser.add_argument(
        'x1',
        type=int,
        help='X position of top left'
    )
    parser.add_argument(
        'y1',
        type=int,
        help='Y position of top left'
    )
    parser.add_argument(
        'x2',
        type=int,
        help='X position of bottom right'
    )
    parser.add_argument(
        'y2',
        type=int,
        help='Y position of bottom right'
    )
    args = parser.parse_args()
    filename = args.filename
    x1 = args.x1
    y1 = args.y1
    x2 = args.x2
    y2 = args.y2


    linesLocation, listOfResults = pipeline(filename, (x1, y1), (x2, y2))
    for (loc, result) in zip(linesLocation, listOfResults):
        print('from {} to {} : {}'.format(loc[0], loc[1], result))