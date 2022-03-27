from flask import Flask,render_template,request,redirect,url_for
from forms import LoginForm, RegistrationForm
from GoogleNews import GoogleNews
import json 
import os
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from flask_login import LoginManager, current_user, login_required
import psycopg2
import json
# from newsapi import NewsApiClient

googlenews_flu = GoogleNews()
app= Flask(__name__)

app.config['SECRET_KEY']='mysecretkey'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://eiqzfvvlvdztui:c45d72b394b6727afbb71db71c4d4a312880e86e0fec5ab92e40db84fbaf1fc8@ec2-44-194-92-192.compute-1.amazonaws.com:5432/d88kt7tsccnlar'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app, session_options={"autoflush": False})

Migrate(app,db)

# login_manager=LoginManager()
# login_manager.init_app(app)
# login_manager.login_view='users.login'

mynews_malaria=[]
mynews_hep=[]
mynews_flu=[]
no_of_cases="--"
cases_mal="10"



act_user="REGISTER"
act_admin="LOGIN"

@app.route('/',methods=["GET","POST"])
def user():
    form=RegistrationForm()
    if form.submit2.data and form.validate():
        print(form.data)
        next=url_for('reg_success')
        return redirect(next)

    
    return render_template('home.html',action=act_user,form=form)

@app.route('/query',methods=["GET","POST"])
def query():
    confirmation="Message Sent "
    name=request.args.get('name')
    contact=request.args.get('contact')
    msg=request.args.get('msg')
    
    # resp=Response()
    print(name,contact,msg)
    # if response.status_code==200:
    #     confirmation="Message sent succesfully!"
    # else:
    #     confirmation="Please try again!"
    render_template ('home.html',confirmation=confirmation)
    return redirect(url_for('user')+"#contact")
    

    

@app.route('/admin',methods=["GET","POST"])
def admin():
    form=LoginForm()
    if form.submit1.data and form.validate():
        print(form.data['email'])
        next=url_for('loggedin')
        return redirect(next)

    return render_template('home.html',action=act_admin,form=form)

@app.route('/success')
def reg_success():
    return render_template('register_success.html')

@app.route('/loggedin')
def loggedin():
    return render_template('admin.html')

@app.route('/newsMalaria')
def newsmal():
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

    return render_template('news.html',context=mynews_malaria)

@app.route('/newsHep')
def newshep():
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

    return render_template('news.html',context=mynews_hep)

@app.route('/newsFlu')
def newsflu():
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

    return render_template('news.html',context=mynews_flu)

@app.route('/adminDashboard')
def dash():
    return render_template("dashboard.html",cases=no_of_cases)

if __name__=='__main__':
    db.create_all()
    app.run(debug=True)