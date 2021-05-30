from flask import Flask, request, jsonify
import numpy as np
import cv2 as cv
import base64

app = Flask(__name__)
# app.config["DEBUG"] = True



books = [
    {'id': 0,
     'title': 'A Fire Upon the Deep',
     'author': 'Vernor Vinge',
     'first_sentence': 'The coldsleep itself was dreamless.',
     'year_published': '1992'},
    {'id': 1,
     'title': 'The Ones Who Walk Away From Omelas',
     'author': 'Ursula K. Le Guin',
     'first_sentence': 'With a clamor of bells that set the swallows soaring, the Festival of Summer came to the city Omelas, bright-towered by the sea.',
     'published': '1973'},
    {'id': 2,
     'title': 'Dhalgren',
     'author': 'Samuel R. Delany',
     'first_sentence': 'to wound the autumnal city.',
     'published': '1975'}
]


@app.route('/', methods=['GET'])
def home():
    return "<h1>Hola Mundo con POST</h1>"


@app.route("/api/v1/resources/books/all", methods=['GET'])
def api_all():
    return jsonify(books)


@app.route("/test", methods=['GET', "POST"])
def testPost():
    if request.method == "POST":
        aux = request.form["img"]
        return aux + "Con Exito"
    else:
        return "Error en el formato"

@app.route("/opencv", methods=['GET', "POST"])
def testPost():
    if request.method == "POST":
        aux = request.form["img"]
        img_decode = base64.b64decode(aux)
        image_result = open("./data/img.jpeg", "wb")
        image_result.write(img_decode)

        img = cv.imread("./data/img.jpeg")

        hsvim = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        lower = np.array([0, 48, 80], dtype="uint8")
        upper = np.array([20, 255, 255], dtype="uint8")
        skinRegionHSV = cv.inRange(hsvim, lower, upper)
        blurred = cv.blur(skinRegionHSV, (2, 2))
        ret, thresh = cv.threshold(blurred, 0, 255, cv.THRESH_BINARY)

        contours, hierarchy = cv.findContours(
            thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        contours = max(contours, key=lambda x: cv.contourArea(x))
        cv.drawContours(img, [contours], -1, (255, 255, 0), 2)

        hull = cv.convexHull(contours, returnPoints=False)
        defects = cv.convexityDefects(contours, hull)

        if defects is not None:
            cnt = 0
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i][0]
            start = tuple(contours[s][0])
            end = tuple(contours[e][0])
            far = tuple(contours[f][0])
            a = np.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
            b = np.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
            c = np.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
            angle = np.arccos((b ** 2 + c ** 2 - a ** 2) /
                            (2 * b * c))
            if angle <= np.pi / 2:
                cnt += 1
                cv.circle(img, far, 4, [0, 0, 255], -1)
        if cnt > 0:
            cnt = cnt+1
        cv.putText(img, str(cnt), (0, 50), cv.FONT_HERSHEY_SIMPLEX,
                1, (255, 0, 0), 2, cv.LINE_AA)

        return cnt
    else:
        return "Error en el formato"



@app.route("/api/v1/resources/books", methods=['GET'])
def api_filter():

    if "id" in request.args:
        id = int(request.args["id"])
    else:
        return "Error: No se proporciono una ID"

    results = []
    for book in books:
        if book["id"] == id:
            results.append(book)
    return jsonify(results)


if __name__ == '__main__':
    app.run(port=80, debug=True)
