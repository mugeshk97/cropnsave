import os
import cv2
import numpy as np
import sys
import uuid

supported_extensions = ['tif', 'tiff', 'TIF', 'TIFF']

path = input("Enter the path to the image dir: ")
if not os.path.exists(path):
    print("[INFO] --> Path does not exist")
    sys.exit()
else:
    files = {}
    idx = 0
    for filename in sorted(os.listdir(path)):
        if filename.split('.')[-1] in supported_extensions:
            files[idx] = os.path.join(path, filename)    
            idx += 1
    if len(files) == 0:
        print(f"[INFO] --> No files found in the path  {path}")
        sys.exit()
    else:
        print(f"[INFO] --> Found {len(files)} files in the path  {path}")

save_path = input("Enter the path to save the cropped images: ")
if not os.path.exists(save_path):
    os.makedirs(save_path)


j = 0
first_crop = False

def mouse_click(event, x, y, flags, param):
    global x1, y1, x2, y2, cropping
    if event == cv2.EVENT_LBUTTONDOWN:
        x1, y1 = x, y
    elif event == cv2.EVENT_LBUTTONUP:
        x2, y2 = x, y

def crop(img, filename, x1, y1, x2, y2):
    try:
        croped = img[y1:y2, x1:x2]
        cv2.imwrite(filename+'.jpg', croped)
        return True
    except Exception as e:
        print(f"[ERROR] --> {e}")

cv2.namedWindow('image') 
cv2.setMouseCallback('image', mouse_click)


while j < len(files):
    global x1, y1, x2, y2
    img = cv2.imread(files[j])

    cv2.setWindowTitle("image", files[j])
    img_copy = img.copy()
    img_copy = cv2.resize(img_copy, (720, 920), interpolation = cv2.INTER_CUBIC)
    if first_crop:
        cv2.rectangle(img_copy, (x1, y1), (x2, y2), (0, 255, 0), 1)
    cv2.imshow('image', img_copy)    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        cv2.destroyAllWindows()
        break
    if key == 13:
        if x1 < x2 and y1 < y2:
            first_crop = True
            filename = files[j].split('/')[-1].split('.')[0]
            random_id = str(uuid.uuid4())
            
            x3 = int(np.interp(x1, [0, img_copy.shape[1]], [0, img.shape[1]]))
            x4 = int(np.interp(x2, [0, img_copy.shape[1]], [0, img.shape[1]]))
            y3 = int(np.interp(y1, [0, img_copy.shape[0]], [0, img.shape[0]]))
            y4 = int(np.interp(y2, [0, img_copy.shape[0]], [0, img.shape[0]]))

            crop(img, save_path+'/'+filename+'_'+random_id, x3, y3, x4, y4)

    if key == ord('n'):
        j += 1
    if key == ord('p'):
        j -= 1
    if j < 0:
        j = 0
    if j >= len(files):
        j = len(files) - 1

