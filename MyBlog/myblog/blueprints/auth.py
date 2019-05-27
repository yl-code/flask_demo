from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user

from myblog.forms import LoginForm
from myblog.models import Admin
from myblog.utils import redirect_back


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:  # 已经登录的用户还发送了 login 的请求
        return redirect_back(url_for("blog.index"))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data

        admin = Admin.query.first()
        if admin:
            if username == admin.username and admin.validate_password(password):
                login_user(admin, remember)
                flash("欢迎您，{}".format(username), "success")
                return redirect_back()
            flash("用户名或密码不正确", "warning")
        else:
            flash("账户不存在", "warning")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("注销成功", "info")
    return redirect_back()

