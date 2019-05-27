from flask import url_for, current_app
from flask_mail import Message
from myblog.extensions import mail
from threading import Thread


def _send_async_mail(app, message):
    """
    使用app_context方法创建一个应用上下文，因为mail.send内部调用了current_app变量，
    这个变量只有在激活的程序上下文中才存在。这里在后台线程调用的send函数，但是后台线程没有程序上下文，
    这里用app.context手动激活上下文

    :param app:
    :param message:
    :return:
    """
    with app.app_context():
        mail.send(message)


def send_mail(subject, to, html):
    """
    构建发送mail的函数
    :param subject: 主题
    :param to: 接收方
    :param html: 发送的HTML内容
    :return:
    """
    app = current_app._get_current_object()  # 通过这样可以获得程序实例
    message = Message(subject, recipients=[to], html=html)
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr


def send_new_comment_mail(post):
    post_url = url_for("blog.show_post", post_id=post.id, _external=True) + "#comments"
    send_mail(subject="新的评论", to=current_app.config["MAIL_USERNAME"],
              html="""
              <p>New comment in post <i>%s</i>, click the link below to check:</p>
              <p><a href="%s">%s</a></P>
              <p><small style="color: #868e96">Do not reply this email.</small></p>
              """ % (post.title, post_url, post_url))


def send_new_reply_email(comment):
    post_url = url_for('blog.show_post', post_id=comment.post_id, _external=True) + '#comments'
    send_mail(subject='新的回复', to=comment.email,
              html='<p>New reply for the comment you left in post <i>%s</i>, click the link below to check: </p>'
                   '<p><a href="%s">%s</a></p>'
                   '<p><small style="color: #868e96">Do not reply this email.</small></p>'
                   % (comment.post.title, post_url, post_url))



















