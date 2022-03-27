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
    
    submit3=SubmitField('Submit')
    submit1=SubmitField('Login')

class RegistrationForm(FlaskForm):
    name=StringField('name', validators=[DataRequired()],render_kw={"placeholder": "Name"})
    company=StringField('company name', validators=[DataRequired()],render_kw={"placeholder": "Company Name"})
    email=StringField('email',validators=[DataRequired(),Email()],render_kw={"placeholder": "Email ID"})
    category = SelectField('category', choices=[('Health Centers','Health Centers'),('Pharmacy','Pharmacy'), ('Hospital','Hospital')],validators=[DataRequired()],render_kw={"placeholder": "Category"})
    phone=StringField('contact no.', validators=[DataRequired()],render_kw={"placeholder": "Contact No."})
    address=StringField('company address', validators=[DataRequired()],render_kw={"placeholder": "Address"})
    
    submit3=SubmitField('Submit')
    submit2=SubmitField('Register as preCURE member')

    # def check_email(self, field):
    #     if User.query.filter_by(email=field.data).first():
    #         raise ValidationError("Your email has been registered already")
