from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/static/<path:path>')
def woo(path):
    return send_from_directory('static', path)

@app.route("/")
def hello():
    return render_template("index.html")

@socketio.on('connect')
def doit():
    print("connected")

@socketio.on('input')
def input_message(message):
    emit('output', {"action":message['action'],"value":message['value'], "timestamp":message["timestamp"]}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
