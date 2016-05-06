#! /usr/env python
# -*- coding: utf-8 -*-

import gevent
from gevent import monkey
import urllib
import os
import time
import requests
from flask_socketio import SocketIO, join_room, leave_room, rooms
from flask import Flask, render_template, request, g
monkey.patch_all()

app = Flask(__name__)
app.debug = True
socketio = SocketIO(app, async_mode='gevent')
BASEPATH = os.path.dirname(__file__)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def connect():
    join_room(request.sid)
    socketio.emit('connect', 'connect success')

@socketio.on('disconnect')
def connect():
    leave_room(request.sid)
    socketio.emit('disconnect', 'disconnect success')

@socketio.on('getphoto')
def getPhoto(name):
    list = [
        gevent.spawn(getName, name['name'], request.sid)
    ]
    if len(name['name']) == 10:
        list.append(gevent.spawn(getJwzx, name['name'], request.sid))
        list.append(gevent.spawn(getCET, name['name'], request.sid))
    gevent.joinall(list)


def getJwzx(name, sid):
    imageName = 'jwzx' + name+'.jpg'
    if os.path.exists(BASEPATH+'/static/'+imageName) is False:
        url = 'http://jwzx.cqupt.edu.cn/showstuPic.php?xh=' + name
        r = requests.get(url, stream=True)
        img = r.content
        try:
            with open(BASEPATH+'/static/'+imageName, "wb") as jpg:
                jpg.write(img)
        except IOError as e:
            print(e)
    socketio.emit('getjwzx', imageName, room=sid)


def getCET(name, sid):
    imageName = 'cet' + name + '.jpg'
    if os.path.exists(BASEPATH + '/static/' + imageName) is False:
        url = 'http://172.22.80.212/PHOTO0906CET/' + name + '.JPG'
        r = requests.get(url, stream=True)
        img = r.content
        try:
            with open(BASEPATH + '/static/' + imageName, "wb") as jpg:
                jpg.write(img)
        except IOError as e:
            print(e)
    socketio.emit('getcet', imageName, room=sid)


def getName(name, sid):
    utf8Data = name
    unicodeData = utf8Data.decode("UTF-8")
    gbkData = unicodeData.encode("GBK")
    url = 'http://jwzx.cqupt.edu.cn/pubBjStu.php?searchKey=' + urllib.quote_plus(gbkData)
    r = requests.get(url)
    r.encoding = 'gbk'
    socketio.emit('getname', r.text, room=sid)

if __name__ == '__main__':
    server = socketio.run(app)