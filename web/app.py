from flask import Flask, render_template, Response, request
from flask_socketio import SocketIO

import cv2
import os

from web.utils.cam import ThreadedCamera
from web.utils.connection import sqliteConnect
from web.utils.database import Database

app = Flask(__name__)
socketio = SocketIO(app)

conn = sqliteConnect()
database = Database(conn)
database.create_table()

lastName = ''
ocupacao = ''
saveface = False
savefaceC = 0
message = ''
progress = 0

cam = ThreadedCamera(src="http://192.168.0.104:4747/video")
face_cascade = cv2.CascadeClassifier('../haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()

def creatDir(name, path=''):
  if not os.path.exists(f'{path}/{name}'): 
    os.makedirs(f'{path}/{name}')  

def saveImg(img):
  global lastName
  global ocupacao
  
  qtd = os.listdir(f'../uploads/{lastName}')
  cv2.imwrite(f'../uploads/{lastName}/{str(len(qtd))}.jpg', img)  

@app.route('/', methods=['GET', 'POST'])
def face_cadastro():
  global saveface  
  global lastName
  global ocupacao
  global message
  
  if request.method == "POST":
    nome = request.form.get('nome')
    matricula = request.form.get('matricula')
    ocp = request.form.get('ocupacao')
    
    saveface = True  
    name = nome  
    lastName = name 
    ocupacao = ocp
    
    if saveface:
      creatDir(name, "../uploads")
      
    database.insert(nome, matricula, ocupacao)

  return render_template('face_cadastro.html', video_loading=saveface)

@app.route('/face_list_users', methods=['GET'])
def face_list_user():
  return render_template("face_list_users.html", users=database.select())
  
def generate_frames():
  
  global saveface
  global savefaceC
  global message
  global progress
  
  while True:
    _, frame = cam.get()
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 6)
    
    for x,y,w,h in faces:
      cv2.rectangle(frame,(x,y),(x+w,y+h),(255,255,255),2)
      roi_gray = gray[y:y+h, x:x+w]
      resize = cv2.resize(roi_gray, (400, 400)) 
      
      if saveface:
        cv2.putText(frame,str(savefaceC),(10,80), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),1,cv2.LINE_AA)
        savefaceC += 1
        saveImg(resize)
        
      if savefaceC > 50:
        savefaceC = 0
        saveface = False
        message = 'sucesso'
        
    _, buffer = cv2.imencode('.jpg', frame)
    frame = buffer.tobytes()
    yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    socketio.emit('message', { 'message': message })
  
@app.route('/video_feed')
def video_feed():
  return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
  socketio.run(debug=True)