from flask import Flask,render_template,request,redirect,url_for,flash
from flask_mail import Message,Mail
from forms import LoginForm, RegistrationForm,SendtoAll,SendtoH,SendtoP,SendtoHC,QueryForm,UpdateForm
from GoogleNews import GoogleNews
import json 
import os
import datetime
from flask_sqlalchemy import SQLAlchemy
import vonage
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_required,logout_user
import psycopg2
import json
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin,LoginManager,login_user,login_required
from datetime import datetime
import smtplib, ssl
import tensorflow as tf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from dash import dcc
import pickle

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "akshararuhi@gmail.com"  # Enter your address
receiver_email = "akshararuhi@gmail.com"  # Enter receiver address
password = 'eqcuvazykyhktnet'


# from newsapi import NewsApiClient
state="malaria"
googlenews_flu = GoogleNews()
login_manager=LoginManager()


app= Flask(__name__)


client = vonage.Client(key="491a6f61", secret="y8iYjGHmpmSv8FKp")
sms = vonage.Sms(client)

app.config['SECRET_KEY']='mysecretkey'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://eiqzfvvlvdztui:c45d72b394b6727afbb71db71c4d4a312880e86e0fec5ab92e40db84fbaf1fc8@ec2-44-194-92-192.compute-1.amazonaws.com:5432/d88kt7tsccnlar'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app,session_options={"autoflush": False})

Migrate(app,db)
login_manager.init_app(app)
login_manager.login_view='home'

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(user_id)

# Models
class Admin(db.Model, UserMixin):
    __tablename__='admin'
    id=db.Column(db.Integer, primary_key=True)
    admin_name=db.Column(db.String(64))
    email=db.Column(db.String(64), unique=True, index=True)
    password_hash=db.Column(db.String(128))

    def __init__(self,name, email, password):
        self.admin_name=name
        self.email=email
        self.password_hash=generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
        

class User(db.Model, UserMixin):
    __tablename__='users'
    id=db.Column(db.Integer, primary_key=True)
    user_name=db.Column(db.String(64))
    phone=db.Column(db.String(64))
    email=db.Column(db.String(64), unique=True, index=True)
    category=db.Column(db.String(128))
    org_name=db.Column(db.String(64))
    org_address=db.Column(db.String(64))

    def __init__(self, name,phone, email, category, oname, oaddress):
        self.user_name=name
        self.phone=phone
        self.email=email
        self.category=category
        self.org_name=oname
        self.org_address=oaddress
    

mynews_malaria=[]
mynews_hep=[]
mynews_flu=[]




identity=''
act_user="REGISTER"
act_admin="LOGIN"

model = tf.keras.models.load_model(r"mal-model")
model1 = tf.keras.models.load_model(r"hep-model")
model2 = tf.keras.models.load_model(r"flu-model")

model3 = pickle.load(open('class_inf_model.pkl', 'rb'))
model4 = pickle.load(open('class_mal_model.pkl', 'rb'))
model5 = pickle.load(open('class_hep_model.pkl', 'rb'))

# connection = db.session.connection()
DATABASE_URL = "postgres://eiqzfvvlvdztui:c45d72b394b6727afbb71db71c4d4a312880e86e0fec5ab92e40db84fbaf1fc8@ec2-44-194-92-192.compute-1.amazonaws.com:5432/d88kt7tsccnlar"
conn = psycopg2.connect(DATABASE_URL, sslmode = 'require')

conn.autocommit = True
cursor = conn.cursor()
#Functions
def get_data_from_sql_mal():
    sql = '''select week, cases from malaria order by id desc limit 50'''
    cursor.execute(sql)


    dates = []
    cases = []

    for i in cursor.fetchall():
        dates.append(i[0])
        cases.append(i[1])
    
    dates.reverse()
    cases.reverse()
    return dates, cases

def get_data_from_sql_hep():
    sql = '''select week, cases from hepatitis order by id desc limit 50'''
    cursor.execute(sql)


    dates = []
    cases = []

    for i in cursor.fetchall():
        dates.append(i[0])
        cases.append(i[1])
    
    dates.reverse()
    cases.reverse()
    return dates, cases

def get_data_from_sql_flu():
    sql = '''select week, cases from influenza order by id desc limit 50'''
    cursor.execute(sql)


    dates = []
    cases = []

    for i in cursor.fetchall():
        dates.append(i[0])
        cases.append(i[1])
    
    dates.reverse()
    cases.reverse()
    return dates, cases

def forecasting_mal(cases, seq_size = 5):
    prev = cases[-seq_size:]
    x_input = np.array(prev)
    x_input = x_input.astype(float)
    temp_input = list(x_input)
    
    lst_output = []
    i=0

    while(i<5):
        if(len(temp_input)>5):
            x_input = np.array(temp_input[1:])
            print("{} week input {}".format(i, x_input))
            x_input = x_input.reshape((1, 1, seq_size))
            yhat = model.predict(x_input, verbose = 2)
            print("{} week output {}".format(i, yhat))
            temp_input.append(yhat[0][0])
            temp_input = temp_input[1:]
            lst_output.append(yhat[0][0])
            i = i+1
        else:
            x_input = x_input.reshape((1, 1, seq_size))
            yhat = model.predict(x_input, verbose = 2)
            print(yhat[0])
            temp_input.append(yhat[0][0])
            lst_output.append(yhat[0][0])
            i = i+1
    
    for i in range(len(lst_output)):
        if lst_output[i]<0:
            lst_output[i] = 0
    
    return lst_output

def forecasting_hep(cases, seq_size = 5):
    prev = cases[-seq_size:]
    x_input = np.array(prev)
    x_input = x_input.astype(float)
    temp_input = list(x_input)
    
    lst_output = []
    i=0

    while(i<5):
        if(len(temp_input)>5):
            x_input = np.array(temp_input[1:])
            print("{} week input {}".format(i, x_input))
            x_input = x_input.reshape((1, 1, seq_size))
            yhat = model1.predict(x_input, verbose = 2)
            print("{} week output {}".format(i, yhat))
            temp_input.append(yhat[0][0])
            temp_input = temp_input[1:]
            lst_output.append(yhat[0][0])
            i = i+1
        else:
            x_input = x_input.reshape((1, 1, seq_size))
            yhat = model1.predict(x_input, verbose = 2)
            print(yhat[0])
            temp_input.append(yhat[0][0])
            lst_output.append(yhat[0][0])
            i = i+1
    
    for i in range(len(lst_output)):
        if lst_output[i]<0:
            lst_output[i] = 0
    
    return lst_output

def forecasting_flu(cases, seq_size = 5):
    prev = cases[-seq_size:]
    x_input = np.array(prev)
    x_input = x_input.astype(float)
    temp_input = list(x_input)
    
    lst_output = []
    i=0

    while(i<5):
        if(len(temp_input)>5):
            x_input = np.array(temp_input[1:])
            print("{} week input {}".format(i, x_input))
            x_input = x_input.reshape((1, 1, seq_size))
            yhat = model2.predict(x_input, verbose = 2)
            print("{} week output {}".format(i, yhat))
            temp_input.append(yhat[0][0])
            temp_input = temp_input[1:]
            lst_output.append(yhat[0][0])
            i = i+1
        else:
            x_input = x_input.reshape((1, 1, seq_size))
            yhat = model2.predict(x_input, verbose = 2)
            print(yhat[0])
            temp_input.append(yhat[0][0])
            lst_output.append(yhat[0][0])
            i = i+1
    
    for i in range(len(lst_output)):
        if lst_output[i]<0:
            lst_output[i] = 0
    
    return lst_output

def get_plot(dates, cases, lst_output):
    forecast_dates = pd.date_range(dates[-1], periods = 5, freq = '1W')
    forecast_dates = forecast_dates.strftime('%Y-%m-%d')
    date_df = pd.to_datetime(pd.Series(dates), format = '%Y-%m-%d')
    date_df = date_df.dt.strftime('%Y-%m-%d')
    print(type(lst_output))
    lstm_output=[ round(x) for x in lst_output ]
    print(lstm_output)
    # for i in lstm_output:
    #     lstm_output[i]=round(lstm_output[i])

    print(lst_output)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=date_df, y=cases,
                    mode='lines',
                    name='Existing Cases'))
    fig.add_trace(go.Scatter(x=forecast_dates, y=lstm_output,
                    mode='lines+markers',
                    name='Forecasted Cases'))
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return fig,lstm_output

def get_proba_inf():
    sql = '''select Precipitation, Temperature, Google, Tweets from influenza order by id desc limit 1'''
    cursor.execute(sql)

    for i in cursor.fetchall():
        prec = i[0]
        temp = i[1]
        google = i[2]
        tweet = i[3]
    
    input_arr = np.array([[prec, temp, tweet, google]]).astype(np.float64)
    prediction = model3.predict_proba(input_arr)
    pred = prediction[0][1]
    return pred
     
def get_proba_mal():
    sql = '''select Precipitation, Temperature, Google, Tweets from malaria order by id desc limit 1'''
    cursor.execute(sql)

    for i in cursor.fetchall():
        prec = i[0]
        temp = i[1]
        google = i[2]
        tweet = i[3]
    
    input_arr = np.array([[prec, temp, tweet, google]]).astype(np.float64)
    prediction = model4.predict_proba(input_arr)
    pred = prediction[0][1]
    
    return pred

def get_proba_hep():
    sql = '''select Precipitation, Temperature, Google, Tweets from hepatitis order by id desc limit 1'''
    cursor.execute(sql)

    for i in cursor.fetchall():
        prec = i[0]
        temp = i[1]
        google = i[2]
        tweet = i[3]
    
    input_arr = np.array([[prec, temp, tweet, google]]).astype(np.float64)
    prediction = model5.predict_proba(input_arr)
    pred = prediction[0][1]
    return pred

#Routes
@app.route('/')
def base():
    return render_template('base.html')

@app.route('/user',methods=["GET","POST"])
def user():
    notif=""
    form=RegistrationForm()
    form1=QueryForm()
    identity='user'
    if form.submit2.data and form.validate():
        print(form.data)
        user_name=form.data['name']
        phone=form.data['phone']
        email=form.data['email']
        category=form.data['category']
        org_name=form.data['company']
        org_address=form.data['address']

        user=User(user_name,phone,email,category,org_name,org_address)

        db.session.add(user)
        db.session.commit()
        next=url_for('reg_success')
        return redirect(next)
        
        
    if form1.submit3.data and form1.validate():
        notif="success_query"
        print(form1.data)


        n=form1.name_q.data
        p=form1.phone_q.data
        e=form1.email_q.data
        msg=form1.message_q.data
        print(n,p,e,msg)
        SUBJECT="Query Regarding preCURE"
        TEXT=" Name :"+n +"\n Contact Number :"+p +"\n Email ID :"+e +"\n Query :"+msg
        message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
        
        print(message)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
        form1.name_q.data=''
        form1.phone_q.data=''
        form1.email_q.data=''
        form1.message_q.data=''
        flash('Message Sent successfully!')
        # next=url_for('user')
        # return redirect(next)

    elif form.submit2.data and form.validate()==False:
        notif="notif"
        for field,errors in form.errors.items():
            notif="notif"
            form.name.data=''
            form.phone.data=''
            form.email.data=''
            form.company.data=''
            form.address.data=''
            print(errors[0])
            err_msg=errors[0]+" Registration Unsuccessful!"
            flash(err_msg)
        

 
          

    elif form1.submit3.data and form1.validate()==False:
        notif="notif"
        form1.name_q.data=''
        form1.phone_q.data=''
        form1.email_q.data=''
        form1.message_q.data=''
        flash("Message not sent..Retry!")
        
        
        

    
    return render_template('home.html',action=act_user,form=form,form1=form1,identity=identity,notif=notif)


@app.route('/admin',methods=["GET","POST"])
def admin():
    notif=""
    form=LoginForm()
    identity='admin'
    if form.submit1.data and form.validate():
        admin=Admin.query.filter_by(email=form.email.data).first()
        
     
        # if admin.check_password(form.password.data) and admin is not None:
        #     login_user(admin)
            
        #     next=url_for('loggedin')
        #     return redirect(next)
        if admin is not None:
            if admin.check_password(form.password.data):
                login_user(admin)
                next=url_for('loggedin')
                return redirect(next)
        elif admin is None:
            notif="notif"
            form.email.data=''
            form.password.data=''
            flash("Please enter the correct credentials and Try Again!")

    elif form.submit1.data and form.validate()==False:
        for field,errors in form.errors.items():
            notif="notif"
            form.email.data=''
            form.password.data=''
            print(errors[0])
            err_msg=errors[0]+" Try Again!"
            flash(err_msg)
        
            
        

    return render_template('home.html',action=act_admin,form=form,identity=identity,notif=notif)

@app.route('/success')
def reg_success():
    return render_template('register_success.html')


@app.route('/loggedin')
@login_required
def loggedin():
    form=UpdateForm()

    return render_template('admin.html',form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin'))

@app.route('/newsMalaria')

def newsmal():
    state='malaria'
    googlenews = GoogleNews(lang='en', region='US')
    googlenews.set_period('7d')

    googlenews.set_encode('utf-8')
    googlenews.get_news('malaria')
    data_malaria=googlenews.results()
    

    

    date_mal = []
    news_mal = []
    img_mal = []
    site_mal=[]
    link_mal=[]


    for i in range(len(data_malaria)):
        newsdata_malaria = data_malaria[i]


        news_mal.append(newsdata_malaria['title'])
        date_mal.append(newsdata_malaria['date'])
        site_mal.append(newsdata_malaria['site'])
        img_mal.append(newsdata_malaria['img'])
        link_mal.append(newsdata_malaria['link'])
        


    
    mynews_malaria = zip(news_mal,date_mal,site_mal, img_mal,link_mal)
    print(len(news_mal))

    return render_template('news.html',context=mynews_malaria,state=state)

@app.route('/newsHep')

def newshep():
    state='hepatitis'
    googlenews_hep = GoogleNews(lang='en', region='US')
    googlenews_hep.set_period('7d')

    googlenews_hep.set_encode('utf-8')
    googlenews_hep.get_news('hepatitis')
    data=googlenews_hep.results()
    print(len(data))

    

    date = []
    news = []
    img = []
    site=[]
    link=[]


    for i in range(len(data)):
        newsdata = data[i]


        news.append(newsdata['title'])
        date.append(newsdata['date'])
        site.append(newsdata['site'])
        img.append(newsdata['img'])
        link.append(newsdata['link'])
        


    
    mynews_hep = zip(news,date,site, img,link)
    print(len(news))

    return render_template('news.html',context=mynews_hep,state=state)

@app.route('/newsFlu')

def newsflu():
    state='flu'
    googlenews_flu = GoogleNews(lang='en', region='US')
    googlenews_flu.set_period('7d')

    googlenews_flu.set_encode('utf-8')
    googlenews_flu.get_news('Flu')
    data=googlenews_flu.results()
    print(len(data))

    

    date = []
    news = []
    img = []
    site=[]
    link=[]


    for i in range(len(data)):
        newsdata = data[i]


        news.append(newsdata['title'])
        date.append(newsdata['date'])
        site.append(newsdata['site'])
        img.append(newsdata['img'])
        link.append(newsdata['link'])
        


    
    mynews_flu = zip(news,date,site, img,link)
    print(len(news))

    return render_template('news.html',context=mynews_flu,state=state)


@app.route('/adminDashboard_malaria')
def malaria():
    state="malaria"
    dates,cases = get_data_from_sql_mal()
    lst_output = forecasting_mal(cases)
    print(lst_output)
    prob=round(get_proba_mal(),2)
    print(prob)
    graph,output=get_plot(dates,cases, lst_output)
    graph1Plot = plotly.offline.plot(graph, 
    config={"displayModeBar": False}, 
    show_link=False, include_plotlyjs=False, 
    output_type='div')
    
    return render_template('dashboard.html',state=state,graph1Plot=graph1Plot,output=output,prob=prob)

@app.route('/adminDashboard_hepatitis')
def hep():
    state="hepatitis"
    dates,cases = get_data_from_sql_hep()
    lst_output = forecasting_hep(cases)
    print(lst_output)
    prob=round(get_proba_hep(),2)
    print(prob)
    graph,output=get_plot(dates,cases, lst_output)
    graph1Plot = plotly.offline.plot(graph, 
    config={"displayModeBar": False}, 
    show_link=False, include_plotlyjs=False, 
    output_type='div')
    

    return render_template('dashboard.html',state=state,graph1Plot=graph1Plot,output=output,prob=prob)

@app.route('/adminDashboard_flu')
def flu():
    state="flu"
    dates,cases = get_data_from_sql_flu()
    lst_output = forecasting_flu(cases)
    print(lst_output)
    prob=round(get_proba_inf(),2)
    print(prob)
    graph,output=get_plot(dates,cases, lst_output)
    graph1Plot = plotly.offline.plot(graph, 
    config={"displayModeBar": False}, 
    show_link=False, include_plotlyjs=False, 
    output_type='div')
    
    return render_template('dashboard.html',state=state,graph1Plot=graph1Plot,output=output,prob=prob)

@app.route('/all',methods=['GET','POST'])

def all():
    state="All"
    idlist=[]
    namelist=[]
    phonelist=[]
    categorylist=[]
    orglist=[]
    orgaddlist=[]
    data=User.query.all()
    form=SendtoAll()

    for ele in data:
        
        id=ele.id
        name=ele.user_name
        phone='91'+ele.phone
        category=ele.category
        org=ele.org_name
        orgadd=ele.org_address
        idlist.append(id)
        namelist.append(name)
        phonelist.append(phone)
        categorylist.append(category)
        orglist.append(org)
        orgaddlist.append(orgadd)

    all_list=zip(idlist,namelist,phonelist,categorylist,orglist,orgaddlist)

    if form.submit_send.data and form.validate:
        # responseData=sms.send_message({
        #                               "from": '919755416505',
        #                               "to": '919892902383',
        #                               "text": "preCURE message testing.",
        #                               })
        # if responseData["messages"][0]["status"] == "0":
        #     print("Message sent successfully.")
        # else:
        #     print(f"Message failed with error: {responseData['messages'][0]['error-text']}") 
        for i in phonelist:
            print(i)
            responseData = sms.send_message(
                {
                  "from": '919755416505',
                  "to": i,
                  "text": "Greetings Health Organization! We at preCURE aim for good health of the society. The number of estimated cases for the disease are 10 hence we request you to be prepared with all the medical neccesities. Regards from Team Precure.",
                })
            if responseData["messages"][0]["status"] == "0":
                print("Message sent successfully.")
            else:
                print(f"Message failed with error: {responseData['messages'][0]['error-text']}")
   
        
    return render_template('dashboard.html',content=all_list,state=state,form=form)

@app.route('/pharma',methods=['GET','POST'])
def pharma():
    state="pharma"
    idlist=[]
    namelist=[]
    phonelist=[]
    categorylist=[]
    orglist=[]
    orgaddlist=[]
    data=User.query.filter_by(category='Pharmacy').all()
    form=SendtoP()

    
    for ele in data:
        
        name=ele.user_name
        phone='91'+ele.phone
        category=ele.category
        org=ele.org_name
        orgadd=ele.org_address
        id=ele.id
        idlist.append(id)
        namelist.append(name)
        phonelist.append(phone)
        categorylist.append(category)
        orglist.append(org)
        orgaddlist.append(orgadd)

    all_list=zip(idlist,namelist,phonelist,categorylist,orglist,orgaddlist)

    if form.submit_send.data and form.validate:
        # responseData=sms.send_message({
        #                               "from": '919755416505',
        #                               "to": '919892902383',
        #                               "text": "preCURE message testing.",
        #                               })
        # if responseData["messages"][0]["status"] == "0":
        #     print("Message sent successfully.")
        # else:
        #     print(f"Message failed with error: {responseData['messages'][0]['error-text']}") 
        for i in phonelist:
            print(i)
            responseData = sms.send_message(
                {
                  "from": '919755416505',
                  "to": i,
                  "text": "Greetings Pharmacy! We at preCURE aim for good health of the society. The number of estimated cases for the disease are 10 hence we request you to stock up the necessary medicines. Regards from Team Precure.",
                })
            if responseData["messages"][0]["status"] == "0":
                print("Message sent successfully.")
            else:
                print(f"Message failed with error: {responseData['messages'][0]['error-text']}")   
        
    return render_template('dashboard.html',content=all_list,state=state,form=form)
@app.route('/healthcenter',methods=['GET','POST'])
def healthcenter():
    state="healthcenter"
    idlist=[]
    namelist=[]
    phonelist=[]
    categorylist=[]
    orglist=[]
    orgaddlist=[]
    data=User.query.filter_by(category='Health Centers').all()
    form=SendtoHC()
    
    for ele in data:
        
        id=ele.id
        name=ele.user_name
        phone='91'+ele.phone
        category=ele.category
        org=ele.org_name
        orgadd=ele.org_address
        idlist.append(id)
        namelist.append(name)
        phonelist.append(phone)
        categorylist.append(category)
        orglist.append(org)
        orgaddlist.append(orgadd)

    all_list=zip(idlist,namelist,phonelist,categorylist,orglist,orgaddlist)

    if form.submit_send.data and form.validate:
        # responseData=sms.send_message({
        #                               "from": '919755416505',
        #                               "to": '919892902383',
        #                               "text": "preCURE message testing.",
        #                               })
        # if responseData["messages"][0]["status"] == "0":
        #     print("Message sent successfully.")
        # else:
        #     print(f"Message failed with error: {responseData['messages'][0]['error-text']}") 
        for i in phonelist:
            print(i)
            responseData = sms.send_message(
                {
                  "from": '919755416505',
                  "to": i,
                  "text": "Greetings Health centers! We at preCURE aim for good health of the society. The number of estimated cases for the disease are 10 hence we request you to be prepared with all the medical neccesities. Regards from Team Precure.",
                })
            if responseData["messages"][0]["status"] == "0":
                print("Message sent successfully.")
            else:
                print(f"Message failed with error: {responseData['messages'][0]['error-text']}")    
        
    return render_template('dashboard.html',content=all_list,state=state,form=form)

@app.route('/hospital',methods=['GET','POST'])
def hospital():
    state="hospital"
    idlist=[]
    namelist=[]
    phonelist=[]
    categorylist=[]
    orglist=[]
    orgaddlist=[]
    data=User.query.filter_by(category='Hospital').all()
    form=SendtoH()
    
    for ele in data:
        id=ele.id
        name=ele.user_name
        phone='91'+ele.phone
        category=ele.category
        org=ele.org_name
        orgadd=ele.org_address
        idlist.append(id)
        namelist.append(name)
        phonelist.append(phone)
        categorylist.append(category)
        orglist.append(org)
        orgaddlist.append(orgadd)

    all_list=zip(idlist,namelist,phonelist,categorylist,orglist,orgaddlist)

    if form.submit_send.data and form.validate:
        # responseData=sms.send_message({
        #                               "from": '919755416505',
        #                               "to": '919892902383',
        #                               "text": "preCURE message testing.",
        #                               })
        # if responseData["messages"][0]["status"] == "0":
        #     print("Message sent successfully.")
        # else:
        #     print(f"Message failed with error: {responseData['messages'][0]['error-text']}") 
        for i in phonelist:
            print(i)
            responseData = sms.send_message(
                {
                  "from": '919755416505',
                  "to": i,
                  "text": "Greetings Health Organization! We at preCURE aim for good health of the society. The number of estimated cases for the disease are 10 hence we request you to ensure the availability of sufficient beds and be prepared with all the medical neccesities. Regards from Team Precure.",
                })
            if responseData["messages"][0]["status"] == "0":
                print("Message sent successfully.")
            else:
                print(f"Message failed with error: {responseData['messages'][0]['error-text']}")    
        
    return render_template('dashboard.html',content=all_list,state=state,form=form)



if __name__=='__main__':
    
    app.run(debug=True)