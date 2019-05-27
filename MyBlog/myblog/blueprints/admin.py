from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint, send_from_directory
from flask_login import login_required, current_user
from flask_ckeditor import upload_success, upload_fail

from myblog.forms import SettingForm, PostForm, CategoryForm, LinkForm
from myblog.models import Post, Comment, Category, Link
from myblog.utils import redirect_back, allowed_file
from myblog.extensions import db

admin_bp = Blueprint("admin", __name__)


@admin_bp.before_request
@login_required
def login_protect():
    """
    为admin蓝本注册一个before_request处理函数，然后为这个函数附加login_required装饰器
    :return:
    """
    pass


@admin_bp.route("/settings", methods=["GET", "POST"])
def settings():
    form = SettingForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.blog_title = form.blog_title.data
        current_user.blog_sub_title = form.blog_sub_title.data
        current_user.about = form.about.data
        db.session.commit()  # extensions中将admin的数据注入到了current_user
        flash("修改成功", "success")
        return redirect(url_for("blog.index"))

    form.name.data = current_user.name
    form.blog_title.data = current_user.blog_title
    form.blog_sub_title.data = current_user.blog_sub_title
    form.about.data = current_user.about
    return render_template("admin/settings.html", form=form)


@admin_bp.route("/post/manage")
def manage_post():
    page = request.args.get("page", 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config["MYBLOG_POST_PAGE_NUM"]
    )
    posts = pagination.items
    return render_template("admin/manage_post.html", page=page, pagination=pagination, posts=posts)


@admin_bp.route("/post/new", methods=["GET", "POST"])
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        category = Category.query.get(form.category.data)  # 这里是存的 category 对象，存 category_id 也OK
        post = Post(title=title, body=body, category=category)
        db.session.add(post)
        db.session.commit()
        flash("博客创建成功", "success")
        return redirect(url_for("blog.show_post", post_id=post.id))
    return render_template("admin/new_post.html", form=form)


@admin_bp.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
def edit_post(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.category = Category.query.get(form.category.data)
        db.session.commit()  # post对象被取出来了，这里就不用session.add了
        flash("博客更新成功", "success")
        return redirect(url_for("blog.show_post", post_id=post_id))
    form.title.data = post.title
    form.body.data = post.body
    form.category.data = post.category_id  # 因为form中的category是一个select单选框
    return render_template("admin/edit_post.html", form=form)


@admin_bp.route("/post/<int:post_id>/delete", methods=["POST"])  # 这就代表只接收POST请求
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)  # 删除博客
    db.session.commit()
    flash("删除成功", "success")
    return redirect_back()


######### 以下为评论的管理 ###########


@admin_bp.route("/post/<int:post_id>/set-comment", methods=["POST"])
def set_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if post.can_comment:
        post.can_comment = False
        flash("禁止评论成功", "success")
    else:
        post.can_comment = True
        flash("允许评论成功", "success")
    db.session.commit()
    return redirect_back()


@admin_bp.route("/comment/<int:comment_id>/approve", methods=["POST"])
def approve_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.reviewed = True  # 评审评论
    db.session.commit()
    flash("评论发表", "success")
    return redirect_back()


@admin_bp.route("/comment/manage")
def manage_comment():
    filter_rule = request.args.get("filter", "all")  # all, unreviewed, admin
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["MYBLOG_POST_PAGE_NUM"]

    # 这里先根据过滤条件取出所有符合条件的评论
    if filter_rule == "unread":
        filtered_comments = Comment.query.filter_by(reviewed=False)
    elif filter_rule == "admin":
        filtered_comments = Comment.query.filter_by(from_admin=True)
    else:
        filtered_comments = Comment.query

    pagination = filtered_comments.order_by(Comment.timestamp.desc()).paginate(page, per_page=per_page)
    comments = pagination.items
    return render_template("admin/manage_comment.html", comments=comments, pagination=pagination)


@admin_bp.route("/comment/<int:comment_id>/delete", methods=["POST"])
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash("评论删除成功", "success")
    return redirect_back()


################# 以下为分类 ###################


@admin_bp.route("/category/manage")
def manage_category():
    return render_template("admin/manage_category.html")


@admin_bp.route("/category/new", methods=["GET", "POST"])
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash("创建分类成功", "success")
        return redirect(url_for("admin.manage_category"))
    return render_template("admin/new_category.html", form=form)


@admin_bp.route("/category/<int:category_id>/edit", methods=["GET", "POST"])
def edit_category(category_id):
    form = CategoryForm()
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash("你没有权利编辑这个默认的分类哦", "warning")
        return redirect(url_for("admin.manage_category"))
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash("分类修改成功", "success")
        return redirect(url_for("admin.manage_category"))

    form.name.data = category.anme
    return render_template("admin/edit_category.html", form=form)


@admin_bp.route("/category/<int:category_id>/delete", methods=["POST"])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash("你的级别不够哦，不能删除这个分类", "warning")
        return redirect(url_for("admin.manage_category"))
    category.delete()  # 删除分类,调用的是Category Model里面的类方法
    flash("删除成功", "success")
    return redirect(url_for("admin.manage_category"))


# 连接管理
@admin_bp.route("/link/manage")
def manage_link():
    return render_template("admin/manage_link.html")


@admin_bp.route("/link/new", methods=["GET", "POST"])
def new_link():
    form = LinkForm()
    if form.validate_on_submit():
        name = form.name.data
        url = form.url.data
        link = Link(name=name, url=url)
        db.session.add(link)
        db.session.commit()
        flash("连接创建成功", "success")
        return redirect(url_for("admin.manage_link"))
    return render_template("admin/new_link.html", form=form)


@admin_bp.route("/link/<int:link_id>/edit", methods=["GET", "POST"])
def edit_link(link_id):
    form = LinkForm()
    link = Link.query.get_or_404(link_id)
    if form.validate_on_submit():
        link.name = form.name.data
        link.url = form.url.data
        db.session.commit()
        flash("链接更新成功", "success")
        return redirect(url_for("admin.manage_link"))
    form.name.data = link.name
    form.url.data = link.url
    return render_template("admin/edit_link.html", form=form)


@admin_bp.route("/link/<int:link_id>/delete", methods=["POST"])
def delete_link(link_id):
    link = Link.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()
    flash("删除成功", "success")
    return redirect(url_for("admin.manage_link"))






















