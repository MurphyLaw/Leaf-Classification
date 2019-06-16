from flask import Flask, jsonify, render_template, Response
from camera_opencv import Camera

app = Flask(__name__)

scanning = True

@app.route('/setting', methods=['GET'])
def set_scanning():
    global scanning
    scanning = True
    return ''

@app.route('/<int:leaf_id>', methods=['GET'])
def get_tasks(leaf_id):
    leafs = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December"
    }
    global scanning
    if scanning:
        return leafs.get(leaf_id, "Not in Model")
    return leafs.get(leaf_id, "Not in Model")


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/pc_video_feed')
def pc_video_feed():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='4000')