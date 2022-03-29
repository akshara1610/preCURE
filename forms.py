from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField, FloatField, DateField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired

from flask_login import current_user
# from Project.models import User

class LoginForm(FlaskForm):
    email=StringField('email',validators=[DataRequired(),Email()],render_kw={"placeholder": "Email ID"})
    password=PasswordField('pwd', validators=[DataRequired()],render_kw={"placeholder": "Password"})
    
    
    submit1=SubmitField('Login')

class RegistrationForm(FlaskForm):
    name=StringField('name', validators=[DataRequired()],render_kw={"placeholder": "Name"})
    company=StringField('company name', validators=[DataRequired()],render_kw={"placeholder": "Company Name"})
    email=StringField('email',validators=[DataRequired(),Email()],render_kw={"placeholder": "Email ID"})
    category = SelectField('category', choices=[('Health Centers','Health Centers'),('Pharmacy','Pharmacy'), ('Hospital','Hospital')],validators=[DataRequired()],render_kw={"placeholder": "Category"})
    phone=StringField('contact no.', validators=[DataRequired()],render_kw={"placeholder": "Contact No."})
    address=StringField('company address', validators=[DataRequired()],render_kw={"placeholder": "Address"})
    
    
    submit2=SubmitField('Register as preCURE member')

    # def check_email(self, field):
    #     if User.query.filter_by(email=field.data).first():
    #         raise ValidationError("Your email has been registered already")

class SendtoAll(FlaskForm):
    submit_send=SubmitField('SEND ALERT TO ALL')

class SendtoP(FlaskForm):
    submit_send=SubmitField('SEND ALERT TO PHARMACIES')

class SendtoH(FlaskForm):
    submit_send=SubmitField('SEND ALERT TO HOSPITALS')

class SendtoHC(FlaskForm):
    submit_send=SubmitField('SEND ALERT TO HEALTH CENTERS')

class QueryForm(FlaskForm):
    name_q=StringField('name_query', validators=[DataRequired()],render_kw={"placeholder": "Name"})
    phone_q=StringField('phone_query', validators=[DataRequired()],render_kw={"placeholder": "Contact No."})
    email_q=StringField('email_query',validators=[DataRequired(),Email()],render_kw={"placeholder": "Email ID"})
    message_q=TextAreaField('message_query',validators=[DataRequired()],render_kw={"placeholder": "Type you Query!"})
    submit3=SubmitField('SUBMIT')