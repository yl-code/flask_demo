from flask import Flask, render_template, request
from myblog.blueprints.admin import admin_bp
from myblog.blueprints.auth import auth_bp
from myblog.blueprints.blog import blog_bp
import os
from myblog.settings import config
from myblog.extensions import bootstrap, db, mail, ckeditor, moment, login_manager, csrf
from myblog.models import Admin, Post, Category, Comment, Link
import click
from flask_wtf.csrf import CSRFError
from flask_login import current_user

def create_app(config_name=None):
    """
    工厂函数，需要输入环境配置参数，默认为开发环境
    """
    if config_name is None:
        config_name = os.getenv("FLASK_CONFIG", "development")

    app = Flask("myblog")
    app.config.from_object(config[config_name])  # 加载配置类

    register_blueprints(app)  # 注册蓝本
    register_extensions(app)  # 注册扩展
    register_template_context(app)  # 注册模板上下文
    register_commands(app)  # 注册自定义命令
    register_errors(app)  # 注册错误处理
    return app


def register_blueprints(app):
    app.register_blueprint(blog_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)


def register_template_context(app):
    @app.context_processor  # 注册模板上下文函数，其返回的模板变量可以在任意模板中使用
    def make_template_context():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()
        links = Link.query.order_by(Link.name).all()

        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None

        return dict(admin=admin, categories=categories, links=links, unread_comments=unread_comments)


def register_commands(app):
    @app.cli.command()
    @click.option("--drop", is_flag=True, help="删除后重新创建")
    def initdb(drop):
        """
        初始化数据库
        :param drop:
        :return:
        """
        if drop:
            click.confirm("这个操作将会删除数据库里面的所有数据哦😯，你想继续吗？", abort=True)
            db.drop_all()
            click.echo("删除成功")
        db.create_all()
        click.echo("重新建立数据表成功")

    @app.cli.command()
    @click.option("--username", prompt=True, help="用于登录博客后台的用户名")
    @click.option("--password", prompt=True, hide_input=True,
                  confirmation_prompt=True, help="用于登录博客后台的密码")
    def init(username, password):
        """
        创建只属于你的博客系统，prompt=True如果用户没有输入选项值，这会以提示符的形式请求输入。
        :param username:
        :param password:
        :return:
        """
        click.echo("初始化数据库...")
        db.create_all()

        admin = Admin.query.first()
        if admin is not None:
            click.echo('已经存在管理员，正在跟新...')
            admin.username = username
            admin.set_password(password)
        else:
            click.echo('创建管理员账户中...')
            admin = Admin(
                username=username,
                blog_title="MyBlog",
                blog_sub_title="It doesn't matter. Everything will be all right.",
                name="杨磊",
                about="做一只会飞的猪.🤑"
            )
            admin.set_password(password)
            db.session.add(admin)

        category = Category.query.first()
        if category is None:
            click.echo('创建文章默认分类中...')
            category = Category(name='default')
            db.session.add(category)

        db.session.commit()
        click.echo('Done.')

    @app.cli.command()
    @click.option('--category', default=5, help='Quantity of categories, default is 5.')
    @click.option('--post', default=10, help='Quantity of posts, default is 10.')
    @click.option('--comment', default=100, help='Quantity of comments, default is 100.')
    def forge(category, post, comment):
        """Generate fake data."""
        from myblog.fakes import fake_admin, fake_categories, fake_posts, fake_comments, fake_links

        db.drop_all()
        db.create_all()

        click.echo('Generating the administrator...')
        fake_admin()

        click.echo('Generating %d categories...' % category)
        fake_categories(category)

        click.echo('Generating %d posts...' % post)
        fake_posts(post)

        click.echo('Generating %d comments...' % comment)
        fake_comments(comment)

        click.echo('Generating links...')
        fake_links()

        click.echo('Done.')


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template("errors/400.html"), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("errors/500.html"), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template("errors/400.html", description=e.description), 400











