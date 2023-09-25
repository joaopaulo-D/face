import tkinter as tk
from PIL import Image, ImageTk

import cv2
import os
import numpy as np

from utils.cam import ThreadedCamera
from utils.loading import ImageLabel
from utils.connection import sqliteConnect
from utils.database import Database

conn = sqliteConnect()
database = Database(conn)

lastName = ''
savefaceC = 0
trained = False
persons = []
cache = {}

cam = ThreadedCamera(src="http://192.168.0.104:4747/video")
face_cascade = cv2.CascadeClassifier('../haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()

def trainData():
  global recognizer  
  global trained
  global persons
  
  trained = True
  persons = os.listdir('../uploads/')  
  ids = []  
  faces = []  
  for i, p in enumerate(persons):  
    i += 1  
    for f in os.listdir(f'../uploads/{p}'):  
      img = cv2.imread(f'../uploads/{p}/{f}', 0)  
      faces.append(img) 
      ids.append(i)  
  recognizer.train(faces, np.array(ids))

def update_frame():
  
  global recognizer
  global trained
  
  _, frame = cam.get()
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  faces = face_cascade.detectMultiScale(gray, 1.3, 6)

  for x, y, w, h in faces:
    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
    roi_gray = gray[y:y + h, x:x + w]
    resize = cv2.resize(roi_gray, (400, 400))
    
    if trained:
      idf, conf = recognizer.predict(resize)
      nameP = persons[idf-1]
      cv2.putText(frame,nameP,(x+5,y+25), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
      cv2.putText(frame,'TREINADO',(10,65), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
      
      if nameP in cache:
        nome, matricula, ocupacao = cache[nameP]
      else:
        response = database.consult(nameP)
        
        if response:
          nome, matricula, ocupacao = response
          cache[nameP] = (nome, matricula, ocupacao)
          
      cv2.putText(frame,f"Nome: {nome}",(10,85), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,255,255),1,cv2.LINE_AA)
      cv2.putText(frame,f"Matricula: {matricula}",(10,110), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,255,255),1,cv2.LINE_AA)
      cv2.putText(frame,f"Ocupacao: {ocupacao.lower()} (A)",(10,130), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,255,255),1,cv2.LINE_AA)
      cv2.putText(frame,f"Acesso: liberado",(10,150), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,0,0),1,cv2.LINE_AA)
      
      # if not (nome and matricula and ocupacao):
      #   cv2.putText(frame,'Pessoa: DESCONHECIDO',(10,85), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1,cv2.LINE_AA)
      #   cv2.putText(frame,'Acesso: nao liberado',(10,65), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,255),1,cv2.LINE_AA)
    else:
      trainData()

  frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
  img = Image.fromarray(frame_rgb)
  img_tk = ImageTk.PhotoImage(image=img)

  label.config(image=img_tk)
  label.image = img_tk
  label.after(10, update_frame)

root = tk.Tk()
root.title('Reconhecimento Facial')

loading_label = ImageLabel(root)
loading_label.load('./assets/img/loading.gif')
loading_label.pack()

def start_video_feed():
  loading_label.destroy() 
  label.pack()
  update_frame()

label = tk.Label(root)

root.after(3000, start_video_feed)

def close_window():
  cam.release()
  root.destroy()

root.protocol("WM_DELETE_WINDOW", close_window)
root.mainloop()