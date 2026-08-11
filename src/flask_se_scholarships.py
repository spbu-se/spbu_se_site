# SPDX-License-Identifier: Apache-2.0

from flask import render_template


def get_scholarships_1():
    return render_template("scholarships/1.html")


def get_scholarships_2():
    return render_template("scholarships/2.html")


def get_scholarships_3():
    return render_template("scholarships/3.html")


def get_scholarships_4():
    return render_template("scholarships/4.html")


def get_scholarships_5():
    return render_template("scholarships/5.html")


def get_scholarships_6():
    return render_template("scholarships/6.html")


def get_scholarships_7():
    return render_template("scholarships/7.html")


def get_scholarships_8():
    return render_template("scholarships/8.html")


def get_scholarships_9():
    return render_template("scholarships/9.html")


def get_scholarships_10():
    return render_template("scholarships/10.html")


def get_scholarships_11():
    return render_template("scholarships/11.html")


def get_scholarships_12():
    return render_template("scholarships/12.html")


def get_scholarships_13():
    return render_template("scholarships/13.html")


def register_routes(app) -> None:
    app.add_url_rule("/scholarships/1.html", view_func=get_scholarships_1)
    app.add_url_rule("/scholarships/2.html", view_func=get_scholarships_2)
    app.add_url_rule("/scholarships/3.html", view_func=get_scholarships_3)
    app.add_url_rule("/scholarships/4.html", view_func=get_scholarships_4)
    app.add_url_rule("/scholarships/5.html", view_func=get_scholarships_5)
    app.add_url_rule("/scholarships/6.html", view_func=get_scholarships_6)
    app.add_url_rule("/scholarships/7.html", view_func=get_scholarships_7)
    app.add_url_rule("/scholarships/8.html", view_func=get_scholarships_8)
    app.add_url_rule("/scholarships/9.html", view_func=get_scholarships_9)
    app.add_url_rule("/scholarships/10.html", view_func=get_scholarships_10)
    app.add_url_rule("/scholarships/11.html", view_func=get_scholarships_11)
    app.add_url_rule("/scholarships/12.html", view_func=get_scholarships_12)
    app.add_url_rule("/scholarships/13.html", view_func=get_scholarships_13)
