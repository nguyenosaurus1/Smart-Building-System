import os
import logging
import eventlet
import json
import pymysql
pymysql.install_as_MySQLdb()
from flask import Flask, render_template, redirect, url_for
from flask_session import Session
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import jsonify, request
import paho.mqtt.publish as publish

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = 'broker.hivemq.com'  # use the free broker from HIVEMQ
app.config['MQTT_BROKER_PORT'] = 1883  # default port for non-tls connection
app.config['MQTT_USERNAME'] = ''  # set the username here if you need authentication for the broker
app.config['MQTT_PASSWORD'] = ''  # set the password here if the broker demands authentication
app.config['MQTT_KEEPALIVE'] = 5  # set the time interval for sending a ping to the broker to 5 seconds
app.config['MQTT_TLS_ENABLED'] = False  # set TLS to disabled for testing purposes

engine = create_engine("mysql://root@localhost/sbs")
db = scoped_session(sessionmaker(bind=engine))

# Check for environment variable
# if not os.getenv("DATABASE_URL"):
#     raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
# engine = create_engine(os.getenv("DATABASE_URL"))
# db = scoped_session(sessionmaker(bind=engine))

mqtt = Mqtt(app)
socketio = SocketIO(app)
bootstrap = Bootstrap(app)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# @app.route('/ui-forms')
# def ui_forms():
#     return render_template('ui-forms.html')

@app.route('/reservation')
def reservation():
    return render_template('book_room.html')

@app.route("/book", methods=['POST'])
def book():
    data = request.form
    db.execute("INSERT INTO reservation VALUES (0,"+data["room_id"]+","+data["period"]+",'truong','"+data["date"]+"')")
    db.commit()
    return render_template('book_room.html')

@app.route("/bookroom", methods=['POST'])
def book_room():
    data = request.form
    date = data["date"]
    period = data["period"]
    rooms = db.execute("SELECT * FROM room")
    json_data=[]
    for room in rooms:
        json_data.append(room["room_id"])

    booked_rooms = db.execute("SELECT * FROM reservation WHERE date='"+date+"' AND period="+period)
    for r in booked_rooms:
        if r["room_id"] in json_data:
            json_data.remove(r["room_id"])
    print(json_data)
    return jsonify(json_data)

@app.route("/set_threshold", methods=['POST'])
def set_threshold():
    data = request.form
    # print(data["light_threshold"])
    # print(data["temp_threshold"])
    # print(data["room_id"])
    # print(type(data["light_threshold"]))
    # print(data["room_id"])
    if data["light_threshold"]:
        db.execute("UPDATE room SET light_threshold="+data["light_threshold"]+" WHERE room_id="+ data["room_id"])
        db.commit()
    if data["temp_threshold"]:
        db.execute("UPDATE room SET temp_threshold="+data["temp_threshold"]+" WHERE room_id="+ data["room_id"])
        db.commit()
    return redirect("/settings")

@app.route("/search-room")
def search_room():
    # global current_user
    # if current_user == 'Guest':
    #     return "Please login"
    return render_template("search_room.html")

@app.route("/device-control")
def search_room_2():
    # global current_user
    # if current_user == 'Guest':
    #     return "Please login"
    return render_template("device-control.html")

@app.route('/get_result', methods=["POST"])
def get_result():
    # floor = int(request.form.get("floor"))
    room = int(request.form.get("room_id"))
   
    try:
        items = db.execute(f"SELECT * FROM device WHERE room_id = {room}").fetchall()
    finally:
        db.close()
    json_data=[]
    # for result in rv:
    #     json_data.append(dict(zip(row_headers,result)))
    # return jsonìy(json_data)
    # return jsonify(rooms)
    for item in items:
        # json_data.append(dict(zip("room_id",room)))
        device = {'device_id': item["device_id"], 'device_name': item["device_name"], 'status': item['status'], 'floor': item['floor'], 'room_id': item['room_id']}
        json_data.append(device)
    print(json_data)
    return jsonify(json_data)
    # return render_template('control_device.html', items=items)

@app.route('/get_toggled_status') 
def toggled_status():
    device_id = request.args.get('device_id')
    current_status = request.args.get('status')
    if current_status != "" and current_status in ["On", "Off"]:
        light = 'OFF' if current_status == 'Off' else 'ON'
        value = 0 if current_status == 'Off' else 1
        print(light)
        print(device_id)
        # split_data = topic.split('/')
        p_data = {}
        p_data["device_id"] = "Light"
        p_data["value"] = light
        data1 = json.dumps([p_data])
        publish.single('Topic/Light', data1, hostname="broker.hivemq.com")

        try:
            db.execute(f"UPDATE device SET status = {value} WHERE device_id = {device_id}")
            db.commit()
            print('Update sucessfully')
        finally:
            db.close()
        return jsonify({"success": True,
                        "msg": "Done"})
    else:
        print('Please try')
        return jsonify({"success": False,
                        "msg": "Done"})

@app.route("/lookuprooms")
def lookup_rooms():
    rooms = db.execute("SELECT * FROM room")
    # row_headers=[x[0] for x in rooms.description] #this will extract row headers
    # rv = rooms.fetchall()
    json_data=[]
    # for result in rv:
    #     json_data.append(dict(zip(row_headers,result)))
    # return jsonìy(json_data)
    # return jsonify(rooms)
    for room in rooms:
        # json_data.append(dict(zip("room_id",room)))
        json_data.append(room["room_id"])
    print(json_data)
    return jsonify(json_data)

# @mqtt.on_connect()
# def handle_connect(client, userdata, flags, rc):
#     #Sub 2 chosen topics 
#     print('on connect')
#     mqtt.subscribe('Topic/TempHumi')
#     mqtt.subscribe('Topic/Mois')

# @mqtt.on_message()
# def handle_mqtt_message(client, userdata, message):
#     topic=message.topic    
#     #data = handle_message(message)
#     print('topic')
#     print('topic123')
#     print('topic214')
#     print(message.payload.decode())
#     print(topic)
#     print(client)
#     print(userdata)
#     print(message)
#     mqtt.publish('Topic/TempHumi','Hello World this is payload')

def handle_message(message):
    payload=json.loads(message.payload.decode())
    data = dict()
    if message.topic == "Topic/TempHumi":
        data = dict(
        temp= payload[0]["values"][0],
        humid= payload[0]["values"][1],
    )
    if message.topic == "Topic/Mois":
        data = dict(
            mois = payload[0]["values"][0],
        )        
    return data

@socketio.on('publish')
def handle_publish(json_str):
    data = json.loads(json_str)
    mqtt.publish(data['topic'], data['message'])
    # print('publish')

@socketio.on('subscribe')
def handle_subscribe(json_str):
    data = json.loads(json_str)
    mqtt.subscribe(data['topic'])
    # print('subcribe')

@socketio.on('unsubscribe')
def handle_unsubscribe(json_str):
    data = json.loads(json_str)
    mqtt.unsubscribe(data['topic'])

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=json.loads(str(message.payload.decode()))
    )
    socketio.emit('mqtt_message', data=data)

# @mqtt.on_message()
# def handle_mqtt_message(client, userdata, message):
#     data = dict(
#         topic=message.topic,
#         payload=message.payload.decode()
#     )
#     room = data['topic'].split("-")[1]
#     print(room)

#     socketio.emit('mqtt_message', data=data)
#     # print(data.payload)
#     if int(data['payload']) > 50:
#         db.execute("""UPDATE device SET status=0 WHERE room_id=:room""", {"room":room})
#         db.commit()
#         data1 = json.loads('{"topic": "' + "light-" + room + '", "message": "' + "0" + '"}')
#         mqtt.publish(data1['topic'], data1['message'])

