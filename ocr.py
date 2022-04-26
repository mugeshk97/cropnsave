from flask import Flask, request, jsonify
import pytesseract
import numpy as np
import cv2
import base64

app = Flask(__name__)

@app.route('/', methods=['GET' , 'POST'])
def index():
    if request.method == 'POST':
        try:
            img_base64 = request.get_json()['img']
            img_decode = base64.b64decode(img_base64)
            img_np = np.frombuffer(img_decode, np.uint8)
            img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, img_thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            text = pytesseract.image_to_string(img_thresh, lang='eng')
            return jsonify(text)
        except Exception as e:
            return jsonify("can't able read image")

if __name__ == '__main__':
    app.run(debug=True)