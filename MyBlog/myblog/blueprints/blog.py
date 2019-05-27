from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint, abort, make_response
from myblog.models import Post, Category, Comment
from flask_login import current_user
from myblog.forms import CommentForm, AdminCommentForm
from myblog.emails import send_new_comment_mail, send_new_reply_email
from myblog.extensions import db
from myblog.utils import redirect_back

blog_bp = Blueprint("blog", __name__)


@blog_bp.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    page_num = current_app.config["MYBLOG_POST_PAGE_NUM"]  # 获取配置参数
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=page_num)
    posts = pagination.items  # flask-sqlalchemy内置的分页功能
    return render_template("blog/index.html", posts=posts, pagination=pagination)


@blog_bp.route("/about")
def about():
    return render_template("blog/about.html")


@blog_bp.route("/category/<int:category_id>")
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get("page", 1, type=int)
    page_num = current_app.config["MYBLOG_POST_PAGE_NUM"]
    pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page, page_num)
    posts = pagination.items
    return render_template("blog/category.html", category=category, pagination=pagination, posts=posts)


@blog_bp.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)   # 若果查询文章不存在，就返回404错误
    page = request.args.get("page", 1, type=int)
    page_num = current_app.config["MYBLOG_POST_PAGE_NUM"]
    pagination = Comment.query.with_parent(post).filter_by(reviewed=True).order_by(Comment.timestamp.desc()).paginate(page, page_num)
    comments = pagination.items

    if current_user.is_authenticated:
        form = AdminCommentForm()
        form.author.data = current_user.name
        form.email.data = current_app.config["MAIL_USERNAME"]
        form.site.data = url_for("blog.index")
        from_admin = True
        reviewed = True
    else:
        form = CommentForm()
        from_admin = False
        reviewed = False

    if form.validate_on_submit():
        author = form.author.data
        email = form.email.data
        site = form.site.data
        body = form.body.data
        comment = Comment(author=author, email=email, site=site, body=body, from_admin=from_admin,
                          post=post, reviewed=reviewed)
        replied_id = request.args.get("reply")
        if replied_id:
            replied_comment = Comment.query.get_or_404(replied_id)
            comment.replied = replied_comment
            send_new_reply_email(replied_comment)  # 邮件通知评论人，该评论有人回复了
        db.session.add(comment)
        db.session.commit()  #

        if current_user.is_authenticated:
            flash("恭喜您，评论成功.🤗", "success")  # 如果当前用户为管理员，则直接发表成功
        else:
            flash("您的评论已经被推送，等待被审查.😇", "info")
            send_new_comment_mail(post)  # 邮件通知文章作者，有新的评论

        return redirect(url_for("blog.show_post", post_id=post_id))
    return render_template("blog/post.html", post=post, pagination=pagination, comments=comments, form=form)


@blog_bp.route("/reply/comment/<int:comment_id>")
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if not comment.post.can_comment:
        flash("博主禁止评论哦.😤", "warning")
        return redirect(url_for("blog.show_post", post_id=comment.post_id))
    return redirect(url_for("blog.show_post", post_id=comment.post_id, reply=comment_id, author=comment.author) + "#comment-form")


@blog_bp.route("/change-theme/<theme_name>")
def change_theme(theme_name):
    if theme_name not in current_app.config["MYBLOG_THEMES"].keys():
        abort(404)
    response = make_response(redirect_back())
    response.set_cookie("theme", theme_name, max_age=30 * 24 * 60 * 60)  # 设置cookie存活时间为30天
    return response












