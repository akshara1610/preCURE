# from app import db
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_login import UserMixin
# from datetime import datetime

# class Admin(db.Model, UserMixin):
#     __tablename__='admin'
#     id=db.Column(db.Integer, primary_key=True)
#     admin_name=db.Column(db.String(64))
#     email=db.Column(db.String(64), unique=True, index=True)
#     password_hash=db.Column(db.String(128))

#     def __init__(self,name, email, password):
#         self.admin_name=name
#         self.email=email
#         self.password_hash=generate_password_hash(password)
        

# class User(db.Model, UserMixin):
#     __tablename__='users'
#     id=db.Column(db.Integer, primary_key=True)
#     user_name=db.Column(db.String(64))
#     phone=db.Column(db.String(64))
#     email=db.Column(db.String(64), unique=True, index=True)
#     category=db.Column(db.String(128))
#     org_name=db.Column(db.String(64))
#     org_address=db.Column(db.String(64))

#     def __init__(self, name,phone, email, category, oname, oaddress):
#         self.user_name=name
#         self.phone=phone
#         self.email=email
#         self.category=category
#         self.org_name=oname
#         self.org_address=oaddress
    