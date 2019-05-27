from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, \
    ValidationError, HiddenField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional, URL

from myblog.models import Category


# 登录表单
class LoginForm(FlaskForm):
    username = StringField("账号", validators=[DataRequired(), Length(1, 20, message="亲，账号长度在1到20之间哦😯")])
    password = PasswordField("密码", validators=[DataRequired(), Length(1, 128)])
    remember = BooleanField("记住我")
    submit = SubmitField("登录")


# 文章表单
class PostForm(FlaskForm):
    title = StringField("标题", validators=[DataRequired(), Length(1, 60)])
    category = SelectField("分类", coerce=int, default=1)
    body = CKEditorField("内容", validators=[DataRequired()])
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category.choices = [  # 分类选项 需要取数据库里面的实时数据
            (category.id, category.name) for category in Category.query.order_by(Category.name).all()
        ]


# 分类表单
class CategoryForm(FlaskForm):
    name = StringField("name", validators=[DataRequired(), Length(1, 30)])
    submit = SubmitField()

    def validate_name(self, field):
        if Category.query.filter_by(name=field.data).first():
            raise ValidationError("亲， 名字已经存在了哦😅🤡😤")


# 普通人评论表单
class CommentForm(FlaskForm):
    author = StringField("姓名", validators=[DataRequired(), Length(1, 30)])
    email = StringField("邮件", validators=[DataRequired(), Email(), Length(1, 50)])
    # optional允许输入值为空，并跳过其他验证，若输入内容，则检查输入的站点是否为URL
    site = StringField("站点", validators=[Optional(), URL(), Length(1, 100)])
    body = TextAreaField("内容", validators=[DataRequired()])
    submit = SubmitField()


# 管理员评论表单
class AdminCommentForm(CommentForm):
    author = HiddenField()
    email = HiddenField()
    site = HiddenField()


# 填写链接的表单
class LinkForm(FlaskForm):
    name = StringField("链接名", validators=[DataRequired(), Length(1, 30)])
    url = StringField("URL", validators=[DataRequired(), Length(1, 100)])
    submit = SubmitField()


# 设置页表单
class SettingForm(FlaskForm):
    name = StringField("姓名", validators=[DataRequired(), Length(1, 30, message="姓名长度在1到30之间，兄弟注意点哦🙃🙃")])
    blog_title = StringField("博客标题", validators=[DataRequired(), Length(1, 60)])
    blog_sub_title = StringField("博客子标题", validators=[DataRequired(), Length(1, 100)])
    about = CKEditorField("关于", validators=[DataRequired()])
    submit = SubmitField()









