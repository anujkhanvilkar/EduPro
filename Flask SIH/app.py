from cgitb import text
from email.policy import default
from flask import Flask, render_template, Response, redirect,request,session,url_for
from flask_sqlalchemy import SQLAlchemy
import cv2
import os
from flask_session import Session
import pandas as pd
import numpy as np
import pytesseract
import face_recognition
import os   
from datetime import datetime
from flask import make_response
import pdfkit
from flask_mail import Mail, Message

app = Flask(__name__,template_folder='template')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ID = ['OPTION A','OPTION B','OPTION C','OPTION D']
app.secret_key = "Huygens0p"
app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'medical0377@gmail.com',
    MAIL_PASSWORD = 'mcdkwxkhxgopanrz',
))
mail = Mail(app)

class quiz(db.Model):
    qno = db.Column(db.Integer, primary_key=True)
    name_of_school=db.Column(db.String(500), nullable=False)
    Class=db.Column(db.String(50), nullable=False)
    Subject_Name=db.Column(db.String(500), nullable=False)
    question = db.Column(db.String(500), nullable=False)
    option_1 = db.Column(db.String(200), nullable=False)
    option_2 = db.Column(db.String(200), nullable=False)
    option_3 = db.Column(db.String(200), nullable=False)
    option_4 = db.Column(db.String(200), nullable=False)
    correct_answer= db.Column(db.String(200), nullable=False)
   
    def __repr__(self) -> str:
        return f"{self.qno} - {self.question}"

class ans(db.Model):
    sno = db.Column(db.Integer, primary_key=True,autoincrement=True)
    question_id=db.Column(db.Integer, db.ForeignKey('quiz.qno'))
    roll_no=db.Column(db.Integer,)
    option = db.Column(db.String(200),default=False)
    right=db.Column(db.Integer,default=None)
    marks=db.Column(db.Integer,)
    #db.UniqueConstraint(roll_no)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.question_id}"


path = 'stud_img'
images = []
classNames = []
myList = os.listdir(path)
print(myList)
name_show=[]
for cl in myList:
  curImg = cv2.imread(f'{path}/{cl}')
  images.append(curImg)
  classNames.append(os.path.splitext(cl)[0])
  print(classNames)
CAMERA = None
CAMERA2=None
a=[]   
def gen_frames():
    global CAMERA
    global text
    global a
    CAMERA = cv2.VideoCapture(0)
    a=[]
    while True:
        pytesseract.pytesseract.tesseract_cmd='C:\\Program Files\\Tesseract-OCR\\tesseract'

        success, frame = CAMERA.read()
        if not success:
            break
        else:
            gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            gaus=cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,115,11)
            thr = cv2.threshold(gray, thresh=0, maxval=255, type=cv2.THRESH_OTSU + cv2.THRESH_BINARY_INV)[1]
            text=pytesseract.image_to_string(thr)
            print(text)
            if len(text) == 12:
               a.append(text)
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            text= 'hello'
            # concat frame one by one and show result
        yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def findEncodings(images):
  encodeList = []
  for img in images:
   img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
   encode = face_recognition.face_encodings(img)[0]
   encodeList.append(encode)
  return encodeList
encodeListKnown = findEncodings(images)




def gen_frames2():
    global CAMERA2
    CAMERA2 = cv2.VideoCapture(0)
    while True:
        success, frame = CAMERA2.read()
        if not success:
            break
        else:
           imgS = cv2.resize(frame,(0,0),None,0.25,0.25)
           imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
 
           facesCurFrame = face_recognition.face_locations(imgS)
           encodesCurFrame = face_recognition.face_encodings(imgS,facesCurFrame)
 
           for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):
                 matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
                 faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
                 matchIndex = np.argmin(faceDis)
 
                 if matches[matchIndex]:
                    name = classNames[matchIndex].upper()
                    print(name)
                    y1,x2,y2,x1 = faceLoc
                    y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
                    cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
                    cv2.rectangle(frame,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
                    cv2.putText(frame,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
            # concat frame one by one and show result
        yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
'''@app.route('/attendance')
def attendance():
  return render_template('attendance.html')'''

@app.route('/video_feed2')
def video_feed2():
    return Response(gen_frames2(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/open2/<int:qno>')
def open2(qno):
    message2 = 'open'
    quizes=quiz.query.filter_by(qno=qno).first()
    return render_template('video.html',message2=[message2],quizes=quizes)

@app.route('/close2/<int:qno>')
def close2(qno):
    if CAMERA2 != None and CAMERA2.isOpened():
        CAMERA2.release()
    #CAMERA.release()
    cv2.destroyAllWindows()
    #nameList.append(name)
    quizes=quiz.query.filter_by(qno=qno).first()
    return render_template('video.html',quizes=quizes)

@app.route('/open/<int:qno>')
def open(qno):
    message = 'open'
    quizes=quiz.query.filter_by(qno=qno).first()
    return render_template('video.html', message=[message],quizes=quizes)

@app.route('/login',methods=['GET','POST'])
def login():
  if request.method=="POST":
       username=request.form['email']
       password=request.form['password']
       if(username=='vaibhavdixit384@gmail.com' and password=='1234'):
           session['email']=username
           return render_template('home.html',email=username)
  else:
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('email',None)
    return render_template('login.html')
@app.route('/close/<int:qno>')
def close(qno):
    if CAMERA != None and CAMERA.isOpened():
        CAMERA.release()
    #CAMERA.release()
    cv2.destroyAllWindows()
    print(a)
    a1=tuple(a)
    print(a1)
    e=[]
    #print(a)
    for u in a1:
        for z in ID:
            if(u.find(z)==-1):
                e.append(u)
    k=tuple(e)
    print(k)
    l=[]
    for v in k:
      if v not in l:
        l.append(v)
    print(l)
    b=tuple(l)
    print(b)
    c=[]
    print(l)
    m=[]
    for i in b:
    #s=str(i.split())
    #print('hello',s)
       print(i)
       k=[int(s) for s in i.split() if s.isdigit()]
       for j in k:
         c.append(j)
       z=[str(s) for s in i.split() if s.isalpha()]
       string_version = " ".join(z)
       m.append(string_version)
       print(c)
       print(m)
       for h in range(len(c)):
        print(h)
        print(len(c))
        #print(g)
        Ans=ans(question_id=qno,roll_no=c[h],option=m[h])
        db.session.add(Ans)
        db.session.commit()
    quizes=quiz.query.filter_by(qno=qno).first()
    return render_template('video.html',quizes=quizes)

@app.route('/mail')
def send_mail():
   todo=ans.query.all()[0]
   msg = Message('Hello', sender = 'medical0377@gmail.com', recipients = ['vaibhavdixit384@gmail.com'])
   s=()
   '''for i in todo:
    k=list(s)
   s=tuple(k)'''
   msg.body = "Your child score is "+str(todo.marks)
   mail.send(msg)
   return render_template('signup.html')

    
@app.route('/ques',methods=['GET', 'POST'])
def ques():
    if request.method=='POST':
        school = request.form['school']
        Class = request.form['class']
        Subject = request.form['subject']
        question = request.form['question']
        option_1 = request.form['option_1']
        option_2 = request.form['option_2']
        option_3 = request.form['option_3']
        option_4 = request.form['option_4']
        correct_answer= request.form['correct_option']
        #todo = Todo(title=title, desc=desc)
        Quiz=quiz(name_of_school=school,Class=Class,Subject_Name=Subject,question=question,option_1=option_1,option_2=option_2,option_3=option_3,option_4=option_4,correct_answer=correct_answer)
        db.session.add(Quiz)
        db.session.commit()
    
    return render_template('new.html')
    
@app.route('/delete/<int:qno>')
def delete(qno):
    todo = ans.query.filter_by(sno=qno).first()
    db.session.delete(todo)
    db.session.commit()
    #ques=None
    #Ans=ans.query.all()
    return redirect('/ans')

@app.route('/show')
def show():
    ques=None
    questions=quiz.query.all() 
    return render_template('show.html',questions=questions,ques=ques)
@app.route('/show_ques/<int:qno>')
def show_ques(qno):
    quizes = quiz.query.filter_by(qno=qno).first()
    return render_template('show_ques.html',quizes=quizes)

@app.route('/ans')
def shans():
  Ans=ans.query.all()
  return render_template('ans.html',Ans=Ans)

@app.route('/result')
def result(qno):
    quizes=quiz.query.filter_by(qno=qno).first()
    Ans=ans.query.all()
    return render_template('result.html',Ans=Ans,quizes=quizes)


@app.route('/calculate/<int:qno>')
def cal(qno):
    i=None
    quizes=quiz.query.filter_by(qno=qno).first()
    per=ans.query.filter_by(sno=qno)
    #print(per[0].option)
    #print(bool(len(per)))
    #print(quizes.correct_answer)
    for i in per:
        #print(i.option)
        if i.option == quizes.correct_answer:
            i.right=1
        else:
            i.right=0
    db.session.add(i)
    db.session.commit()
    todo=ans.query.all()
    return render_template('result.html',todo=todo)

@app.route('/gen_marks',methods=['GET','POST'])
def gen_marks():
    #marks=0
    if request.method=='POST':
       roll_no=request.form['roll_no']
       per=ans.query.filter_by(roll_no=roll_no)
       per2=ans.query.filter_by(roll_no=roll_no)
       #quest=quiz.query.filter_by(qno=per2.question_id)
       for i in per:
          if i.right==1:
              i.marks=5
          else:
             i.marks=0
       db.session.add_all(per)
       db.session.commit()
       ok=ans.query.filter_by(roll_no=roll_no)
       #print(ok)
       return render_template('show_res.html', ok=ok)
    else:
       return render_template('report.html')

if __name__ == "__main__":
    app.run(debug=True, port=8000)
    app.run()