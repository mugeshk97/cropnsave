import os
import cv2
import numpy as np
import sys
import requests
import base64
import pandas as pd

supported_extensions = ['tif', 'tiff', 'TIF', 'TIFF']

if len(sys.argv) == 2:
    type = sys.argv[1]
    if type == 'save' or type == 'both' or type == 'crop':
        print(f"[INFO] --> {type} mode selected")
    else:
        print("[ERROR] --> Invalid argument please use 'save' or 'crop' or 'both'")
        sys.exit()
elif len(sys.argv) > 2:
    print("[ERROR] --> Too many arguments")
    sys.exit()
else:
    print("[ERROR] --> Please provide an argument (save/crop/both)")
    sys.exit()

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
i = 0
first_crop = False

def mouse_click(event, x, y, flags, param):
    global x1, y1, x2, y2, cropping
    if event == cv2.EVENT_LBUTTONDOWN:
        x1, y1 = x, y
    elif event == cv2.EVENT_LBUTTONUP:
        x2, y2 = x, y

def crop(img, filename, x1, y1, x2, y2):
    global i, type
    try:
        croped = img[y1:y2, x1:x2]
        if type == 'save' or type == 'both':
            cv2.imwrite(filename+'.jpg', croped)
        i += 1
        return croped, True
    except Exception as e:
        print(f"[ERROR] --> {e}")

cv2.namedWindow('image') 
cv2.setMouseCallback('image', mouse_click)

data = dict()
df = pd.DataFrame()
while j < len(files):
    global x1, y1, x2, y2
    img = cv2.imread(files[j]) 
    data["filename"] = files[j]
    cv2.setWindowTitle("image", files[j])
    img_copy = img.copy()
    img_copy = cv2.resize(img_copy, (720, 920), interpolation = cv2.INTER_CUBIC)
    if first_crop:
        cv2.rectangle(img_copy, (x1, y1), (x2, y2), (0, 0, 0), 3)
    cv2.imshow('image', img_copy)    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        cv2.destroyAllWindows()
        break
    if key == 13:
        if x1 < x2 and y1 < y2:
            first_crop = True
            filename = files[j].split('/')[-1].split('.')[0]
            x3 = int(np.interp(x1, [0, img_copy.shape[1]], [0, img.shape[1]]))
            x4 = int(np.interp(x2, [0, img_copy.shape[1]], [0, img.shape[1]]))
            y3 = int(np.interp(y1, [0, img_copy.shape[0]], [0, img.shape[0]]))
            y4 = int(np.interp(y2, [0, img_copy.shape[0]], [0, img.shape[0]]))
            croped, ret =crop(img, save_path+'/'+filename+'_'+str(i), x3, y3, x4, y4)
            if ret and (type == 'ocr' or type == 'both'):
                try:
                    request_url = 'http://127.0.0.1:5000/'
                    croped_base64 = cv2.imencode('.jpg', croped)[1].tobytes()
                    croped_base64 = base64.b64encode(croped_base64).decode('utf-8')
                    response = requests.post(request_url, json={'img': croped_base64})
                    print(f"[INFO OCR] --> {response.text}")
                    data["text"+str(i)] = response.text
                    df = df.append(data, ignore_index=True)
                except Exception as e:
                    print(f"[ERROR OCR] --> {e}")
    if key == ord('d'):
        i = 0
        j += 1
    if key == ord('a'):
        i = 0
        j -= 1
    if j < 0:
        j = 0
    if j >= len(files):
        j = len(files) - 1
    pan_size = 10
    # move the crop window
    if key == ord('8'): # up
        y1 -= pan_size
        y2 -= pan_size
    if key == ord('2'): # down
        y1 += pan_size
        y2 += pan_size
    if key == ord('4'): # left
        x1 -= pan_size
        x2 -= pan_size
    if key == ord('6'): # right
        x1 += pan_size
        x2 += pan_size
    # adjust the edge of the crop window
    if key == ord('7'): # top left
        x1 -= pan_size
        y1 -= pan_size
    if key == ord('9'): # top right
        x2 += pan_size
        y1 -= pan_size
    if key == ord('1'): # bottom left
        x1 -= pan_size
        y2 += pan_size
    if key == ord('3'): # bottom right
        x2 += pan_size
        y2 += pan_size
    if key == ord('z'): # reduce top left
        x1 += pan_size
        y1 += pan_size
    if key == ord('x'): # reduce top right
        x2 -= pan_size
        y1 += pan_size
    if key == ord('c'): # reduce bottom left
        x1 += pan_size
        y2 -= pan_size
    if key == ord('v'): # reduce bottom right
        x2 -= pan_size
        y2 -= pan_size
    if key == ord('j'): # download the result
        if not df.empty:
            df.to_csv(save_path+'/'+'data.csv', index=False)
    
