from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class Helloform(FlaskForm):
    name = StringField("姓名", validators=[DataRequired(), Length(1, 20, message="姓名的长度在1到20 之间哦")])
    body = TextAreaField("消息内容", validators=[DataRequired(), Length(1, 100)])
    submit = SubmitField()

