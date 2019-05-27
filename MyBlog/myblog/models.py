from myblog.extensions import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


# 管理员表
class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))          # 账号
    password_hash = db.Column(db.String(128))    # 密码hash值
    blog_title = db.Column(db.String(60))
    blog_sub_title = db.Column(db.String(100))
    name = db.Column(db.String(30))              # 姓名
    about = db.Column(db.Text)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


# 文章分类表
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)  # 文章分类名唯一

    posts = db.relationship("Post", back_populates="category")  # 创建集合关系posts

    def delete(self):
        default_category = Category.query.get(1)
        posts = self.posts[:]
        for post in posts:
            post.category = default_category
        db.session.delete(self)
        db.session.commit()


# 文章表
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # 建立索引
    can_comment = db.Column(db.Boolean, default=True)

    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))  # 外键，一个分类对应多篇文章

    category = db.relationship("Category", back_populates="posts")  # 创建标量关系category
    comments = db.relationship("Comment", back_populates="post", cascade="all, delete-orphan")    # 创建集合关系comments,级联删除


# 评论表
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(30))
    email = db.Column(db.String(50))
    site = db.Column(db.String(100))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # 建立索引

    from_admin = db.Column(db.Boolean, default=False)  # 布尔值，判断是否为管理员的评论
    reviewed = db.Column(db.Boolean, default=False)    # 布尔值，用来检查评论是否通过检查，防止恶意评论

    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))  # 外键，一篇文章对应多个评论
    post = db.relationship("Post", back_populates="comments")  # 创建标量关系post

    replied_id = db.Column(db.Integer, db.ForeignKey("comment.id"))  # 子评论ID, 一个评论对应多个子评论
    replies = db.relationship("Comment", back_populates="replied", cascade="all, delete-orphan")  # 创建集合关系属性，子评论，级联删除
    replied = db.relationship("Comment", back_populates="replies", remote_side=[id])  # 创建标量关系属性，父评论


# 存放链接的表
class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    url = db.Column(db.String(100))






