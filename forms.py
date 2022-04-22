from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField, FloatField, DateField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired
import string

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
    submit_all_mal=SubmitField('Send Alert Regarding Malaria')
    submit_all_hep=SubmitField('Send Alert Regarding Hepatitis')
    submit_all_flu=SubmitField('Send Alert Regarding Influenza')

class SendtoP(FlaskForm):
    submit_p_mal=SubmitField('Send Alert Regarding Malaria')
    submit_p_hep=SubmitField('Send Alert Regarding Hepatitis')
    submit_p_flu=SubmitField('Send Alert Regarding Influenza')

class SendtoH(FlaskForm):
    submit_h_mal=SubmitField('Send Alert Regarding Malaria')
    submit_h_hep=SubmitField('Send Alert Regarding Hepatitis')
    submit_h_flu=SubmitField('Send Alert Regarding Influenza')

class SendtoHC(FlaskForm):
    submit_hc_mal=SubmitField('Send Alert Regarding Malaria')
    submit_hc_hep=SubmitField('Send Alert Regarding Hepatitis')
    submit_hc_flu=SubmitField('Send Alert Regarding Influenza')

class QueryForm(FlaskForm):
    name_q=StringField('name_query', validators=[DataRequired()],render_kw={"placeholder": "Name"})
    phone_q=StringField('phone_query', validators=[DataRequired()],render_kw={"placeholder": "Contact No."})
    email_q=StringField('email_query',validators=[DataRequired(),Email()],render_kw={"placeholder": "Email ID"})
    message_q=TextAreaField('message_query',validators=[DataRequired()],render_kw={"placeholder": "Type you Query!"})
    submit3=SubmitField('SUBMIT')

    

class UpdateForm(FlaskForm):
    cases_mal=StringField('cases_malaria',validators=[DataRequired()] )
    cases_hep=StringField('cases_hep',validators=[DataRequired()] )
    cases_flu=StringField('cases_flu',validators=[DataRequired()] )
    submit4=SubmitField('Update')