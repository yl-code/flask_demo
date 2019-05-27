from flask import request, redirect, url_for, current_app
from urllib.parse import urlparse, urljoin


def is_safe_url(target):
    """
    urlparse模块主要是把url拆分为6部分，并返回元组。

    urljoin主要是拼接URL，它以第一个参数作为其基地址，然后与第二个参数相对地址相结合组成一个绝对URL地址。
    如果它的第二个参数以 //或 http:// 开头即为一个绝对路径，则合成的结果为绝对路径第二个参数。
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def redirect_back(default="blog.index", **kwargs):
    """
    request.referrer为用户所在的原站点URL，但是在很多情况下，referrer字段会为空值，
    比如用户在浏览器的地址栏输入URL，浏览器设置自动清除或者修改 referrer字段

    """
    for target in request.args.get("next"), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
        return redirect(url_for(default, **kwargs))


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in \
            current_app.config["MYBLOG_ALLOWED_IMAGE_EXTENSIONS"]

















