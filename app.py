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
import snscrape.modules.twitter as sntwitter
import itertools
from pytrends.request import TrendReq
from datetime import datetime, timedelta
from meteostat import Point, Daily



port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "akshararuhi@gmail.com"  # Enter your address
receiver_email = "akshararuhi@gmail.com"  # Enter receiver address
password = 'eqcuvazykyhktnet'


# from newsapi import NewsApiClient
state="malaria"
googlenews_flu = GoogleNews()
login_manager=LoginManager()
pytrend = TrendReq()


app= Flask(__name__)


client = vonage.Client(key="5c5ea300", secret="If9duucvNtMDsfrT")
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

tcm=[]
tch=[]
tci=[]




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

def get_date():
    sql = '''select Week from influenza order by id desc limit 1'''

    cursor.execute(sql)
    for i in cursor.fetchall():
        date = i
    date = date[0]
    start_date = date + timedelta(1)
    end_date = start_date + timedelta(6)
    
    return start_date, end_date

def get_id():
    sql = '''select id from influenza order by id desc limit 1'''
    cursor.execute(sql)
    for i in cursor.fetchall():
        id = i[0]
    return id

def get_tweet_count(query, start_date, end_date):
    s = '{} geocode:"43.000000,-75.000000,600km" since:{} until:{}'.format(query, start_date, end_date)
    scraped_tweets = sntwitter.TwitterSearchScraper(s).get_items()
    sliced = itertools.islice(scraped_tweets, 1000000)
    data = pd.DataFrame(sliced)[['date', 'content']]
    count = data.shape[0]
    return count

def get_google_data(ys, ms, ds, ye, me, de):
    all_keywords = ["Malaria", "Hepatitis", "Influenza"]
    cat = '0'
    geo = "US-NY"
    gprop_n = ''
    historical_df = pytrend.get_historical_interest(all_keywords,
                                                year_start = ys,
                                                month_start = ms,
                                                day_start = ds,
                                                hour_start = 0,
                                                year_end = ye,
                                                month_end = me,
                                                day_end = de,
                                                hour_end = 23,
                                                cat = cat,
                                                geo = geo,
                                                gprop = '',
                                                sleep = 0)
    historical_df = historical_df.drop('isPartial', axis = 1)
    historical_df = historical_df.reset_index()
    historical_df['date'] = pd.to_datetime(historical_df['date']).dt.date
    df = historical_df.groupby(['date'])['Malaria', 'Hepatitis', 'Influenza'].sum()
    df = df.reset_index()
    
    mal = 0
    hep = 0
    inf = 0

    for i in df.index:
        mal += df.iloc[i]['Malaria']
        hep += df.iloc[i]['Hepatitis']
        inf += df.iloc[i]['Influenza']

    return int(mal), int(hep), int(inf)

def get_temp_precp(start, end):
    location = Point(40.730610,-73.935242,100)
    data = Daily(location, start, end)
    data = data.fetch()
    data = data[['tavg', 'prcp']]
    twavg = data['tavg'].sum()/7
    pwavg = data['prcp'].sum()/7
    return twavg, pwavg

def insert_influenza(id, end_date, precp, temp, ginf, inf_tweet, inf_cases, inf_epi):
    return cursor.execute('''INSERT INTO influenza(id, Week, Precipitation, Temperature, Google, Tweets, cases, Epidemic) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', (id, end_date, precp, temp, ginf, inf_tweet, inf_cases, inf_epi))

def insert_malaria(id, end_date, precp, temp, gmal, mal_tweet, mal_cases, mal_epi):
    return cursor.execute('''INSERT INTO malaria(id, Week, Precipitation, Temperature, Google, Tweets, cases, Epidemic) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', (id, end_date, precp, temp, gmal, mal_tweet, mal_cases, mal_epi))

def insert_hepatitis(id, end_date, precp, temp, ghep, hep_tweet, hep_cases, hep_epi):
    return cursor.execute('''INSERT INTO hepatitis(id, Week, Precipitation, Temperature, Google, Tweets, cases, Epidemic) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', (id, end_date, precp, temp, ghep, hep_tweet, hep_cases, hep_epi))
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


@app.route('/loggedin',methods=["GET","POST"])
@login_required
def loggedin():
    notif=""
    form=UpdateForm()
    if form.submit4.data and form.validate():
        notif="success_query"
        start_date, end_date = get_date()
        id = get_id() + 1
        sd = start_date.strftime('%Y-%m-%d')
        ed = end_date.strftime('%Y-%m-%d')
        flu_tweet = get_tweet_count('flu', sd, ed)
        inf_tweet = get_tweet_count('influenza', sd, ed)
        mal_tweet = get_tweet_count('malaria', sd, ed)
        hep_tweet = get_tweet_count('hepatitis', sd, ed)
        inf_tweet = inf_tweet + flu_tweet
        ys = start_date.year
        ms = start_date.month
        ds = start_date.day

        ye = end_date.year
        me = end_date.month
        de = end_date.day
        gmal, ghep, ginf = get_google_data(ys, ms, ds, ye, me, de)
        start = datetime.combine(start_date, datetime.min.time())
        end = datetime.combine(end_date, datetime.min.time()) 
        temp, precp = get_temp_precp(start, end)
        inf_cases = form.cases_flu.data
        mal_cases = form.cases_mal.data
        hep_cases = form.cases_hep.data 

        inf_epi = 0
        mal_epi = 0
        hep_epi = 0

        if inf_cases>='220':
            inf_epi = 1

        if mal_cases>='3':
            mal_epi = 1

        if hep_cases>='3':
            hep_epi = 1

        insert_influenza(id, end_date, precp, temp, ginf, inf_tweet, inf_cases, inf_epi)
        insert_malaria(id, end_date, precp, temp, gmal, mal_tweet, mal_cases, mal_epi)
        insert_hepatitis(id, end_date, precp, temp, ghep, hep_tweet, hep_cases, hep_epi)
        form.cases_flu.data=''
        form.cases_hep.data=''
        form.cases_mal.data=''
        flash("Data updated successfully!")

    return render_template('admin.html',form=form,notif=notif)

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
    rounded_value=[ round(x) for x in lst_output ]
    tcm.append(sum(rounded_value))
    print(tcm)
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
    rounded_value=[ round(x) for x in lst_output ]
    tch.append(sum(rounded_value))
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
    rounded_value=[ round(x) for x in lst_output ]
    tci.append(sum(rounded_value))
   
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
    notif=""
    state="All"
    print(tcm)
    text_mal="Greetings Health Organization! We at preCURE aim for good health of the society. The number of estimated cases for  malaria for the next five weeks are nearly "+ str(tcm[0]) +" hence we request you to be prepared with all the medical neccesities. Regards from Team Precure."
    text_hep="Greetings Health Organization! We at preCURE aim for good health of the society. The number of estimated cases for  hepatitis for the next five weeks are nearly "+ str(tch[0]) +" hence we request you to be prepared with all the medical neccesities. Regards from Team Precure."
    text_flu="Greetings Health Organization! We at preCURE aim for good health of the society. The number of estimated cases for  influenza for the next five weeks are nearly "+ str(tci[0]) +" hence we request you to be prepared with all the medical neccesities. Regards from Team Precure."
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

    
    if form.submit_all_mal.data and form.validate:
        notif="success_query"
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
                  "from":  '919892902383',
                  "to": i,
                  "text":text_mal,
                })
            if responseData["messages"][0]["status"] == "0":
                print("Message sent successfully.")
                
            else:
                print(f"Message failed with error: {responseData['messages'][0]['error-text']}")
        flash("Message sent Successfully")

    if form.submit_all_hep.data and form.validate:
        notif="success_query"
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
                  "from":  '919892902383',
                  "to": i,
                  "text":text_hep,
                })
            if responseData["messages"][0]["status"] == "0":
                print("Message sent successfully.")
                
            else:
                print(f"Message failed with error: {responseData['messages'][0]['error-text']}")

        flash("Message sent Successfully")

    if form.submit_all_flu.data and form.validate:
        notif="success_query"
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
                  "from":  '919892902383',
                  "to": i,
                  "text":text_flu,
                })
            if responseData["messages"][0]["status"] == "0":
                print("Message sent successfully.")
                
            else:
                print(f"Message failed with error: {responseData['messages'][0]['error-text']}")

        flash("Message sent Successfully")

    
        
    return render_template('dashboard.html',content=all_list,state=state,form=form,notif=notif)


@app.route('/pharma',methods=['GET','POST'])
def pharma():
    notif=""
    state="pharma"
    text_mal="Greetings Pharmacy! We at preCURE aim for good health of the society. The number of estimated cases for  malaria for the next five weeks are nearly "+ tcm[0] +" hence we request you to be prepared with all the medical neccesities. Regards from Team Precure."
    text_hep="Greetings Pharmacy! We at preCURE aim for good health of the society. The number of estimated cases for  hepatitis for the next five weeks are nearly "+ tch[0] +" hence we request you to be prepared with all the medical neccesities. Regards from Team Precure."
    text_flu="Greetings Pharmacy! We at preCURE aim for good health of the society. The number of estimated cases for  influenza for the next five weeks are nearly "+ tci[0] +" hence we request you to be prepared with all the medical neccesities. Regards from Team Precure."
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

    if form.submit_p_mal.data and form.validate:
        notif="success_query"
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
                  "from":  '919892902383',
                  "to": i,
                  "text": text_mal,
                })
            if responseData["messages"][0]["status"] == "0":
                print("Message sent successfully.")
            else:
                print(f"Message failed with error: {responseData['messages'][0]['error-text']}")

        flash("Message sent Successfully")
            

    if form.submit_p_hep.data and form.validate:
        notif="success_query"
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
                  "from":  '919892902383',
                  "to": i,
                  "text": text_hep,
                })
            if responseData["messages"][0]["status"] == "0":
                print("Message sent successfully.")
                
            else:
                print(f"Message failed with error: {responseData['messages'][0]['error-text']}")

        flash("Message sent Successfully")

    if form.submit_p_flu.data and form.validate:
        notif="success_query"
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
                  "from":  '919892902383',
                  "to": i,
                  "text": text_flu,
                })
            if responseData["messages"][0]["status"] == "0":
                print("Message sent successfully.")
                
            else:
                print(f"Message failed with error: {responseData['messages'][0]['error-text']}") 

        flash("Message sent Successfully")  
        
    return render_template('dashboard.html',content=all_list,state=state,form=form,notif=notif)

@app.route('/healthcenter',methods=['GET','POST'])
def healthcenter():
    notif=""
    state="healthcenter"
    text_mal="Greetings Health Center! We at preCURE aim for good health of the society. The number of estimated cases for  malaria for the next five weeks are nearly "+ tcm[0] +" hence we request you to be prepared with all the medical neccesities. Regards from Team Precure."
    text_hep="Greetings Health Center! We at preCURE aim for good health of the society. The number of estimated cases for  hepatitis for the next five weeks are nearly "+ tch[0] +" hence we request you to be prepared with all the medical neccesities. Regards from Team Precure."
    text_flu="Greetings Health Center! We at preCURE aim for good health of the society. The number of estimated cases for  influenza for the next five weeks are nearly "+ tci[0] +" hence we request you to be prepared with all the medical neccesities. Regards from Team Precure."
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

    if form.submit_hc_mal.data and form.validate:
        notif="success_query"
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
                  "from": ' 919892902383',
                  "to": i,
                  "text": text_mal,
                })
            if responseData["messages"][0]["status"] == "0":
                print("Message sent successfully.")
                
            else:
                print(f"Message failed with error: {responseData['messages'][0]['error-text']}")

        flash("Message sent Successfully")

    if form.submit_hc_hep.data and form.validate:
        notif="success_query"
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
                  "from":  '919892902383',
                  "to": i,
                  "text":text_hep,
                })
            if responseData["messages"][0]["status"] == "0":
                print("Message sent successfully.")
                
            else:
                print(f"Message failed with error: {responseData['messages'][0]['error-text']}")

        flash("Message sent Successfully")

    if form.submit_hc_flu.data and form.validate:
        notif="success_query"
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
                  "from":  '919892902383',
                  "to": i,
                  "text": text_flu,
                })
            if responseData["messages"][0]["status"] == "0":
                print("Message sent successfully.")
                
            else:
                print(f"Message failed with error: {responseData['messages'][0]['error-text']}")  
        flash("Message sent Successfully")  
        
    return render_template('dashboard.html',content=all_list,state=state,form=form,notif=notif)

@app.route('/hospital',methods=['GET','POST'])
def hospital():
    notif=""
    state="hospital"
    text_mal="Greetings Hospital Authority! We at preCURE aim for good health of the society. The number of estimated cases for  malaria for the next five weeks are nearly "+ tcm[0] +" hence we request you to be prepared with all the medical neccesities. Regards from Team Precure."
    text_hep="Greetings Hospital Authority! We at preCURE aim for good health of the society. The number of estimated cases for  hepatitis for the next five weeks are nearly "+ tch[0] +" hence we request you to be prepared with all the medical neccesities. Regards from Team Precure."
    text_flu="Greetings Hospital Authority! We at preCURE aim for good health of the society. The number of estimated cases for  influenza for the next five weeks are nearly "+ tci[0] +" hence we request you to be prepared with all the medical neccesities. Regards from Team Precure."
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

    if form.submit_h_mal.data and form.validate:
        notif="success_query"
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
                  "from": '919892902383',
                  "to": i,
                  "text": text_mal,
                })
            if responseData["messages"][0]["status"] == "0":
                print("Message sent successfully.")
                
            else:
                print(f"Message failed with error: {responseData['messages'][0]['error-text']}")

        flash("Message sent Successfully") 

    if form.submit_h_hep.data and form.validate:
        notif="success_query"
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
                  "from": '919892902383',
                  "to": i,
                  "text": text_hep,
                })
            if responseData["messages"][0]["status"] == "0":
                print("Message sent successfully.")
                
            else:
                print(f"Message failed with error: {responseData['messages'][0]['error-text']}")

        flash("Message sent Successfully")

    if form.submit_h_flu.data and form.validate:
        notif="success_query"
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
                  "from":  '919892902383',
                  "to": i,
                  "text": text_flu,
                })
            if responseData["messages"][0]["status"] == "0":
                print("Message sent successfully.")
                
            else:
                print(f"Message failed with error: {responseData['messages'][0]['error-text']}")   

        flash("Message sent Successfully")
        
    return render_template('dashboard.html',content=all_list,state=state,form=form,notif=notif)



if __name__=='__main__':
    
    app.run()