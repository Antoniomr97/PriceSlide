# Importamos FlaskForm para gestionar los formularios
from flask_wtf import FlaskForm
# Se utiliza para crear textos en formularios, contraseñas y crear boton de envio.
from wtforms import StringField, PasswordField, SubmitField
# EqualTo para comparar las contraseñas, para longitud el length y que el dato no este vacio con DataRequired
from wtforms.validators import DataRequired, Length, EqualTo

# Utilizamos FlaskForm para realizar los formularios
class RegistrationForm(FlaskForm):
    # Marcamos los valores que va tener cada elemento poniendo los datos que requiere
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')