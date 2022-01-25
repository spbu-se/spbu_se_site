# -*- coding: utf-8 -*-

from flask import flash, redirect, request, render_template, url_for


def get_scholarships_1():
    return render_template('scholarships/1.html')


def get_scholarships_2():
    return render_template('scholarships/2.html')


def get_scholarships_3():
    return render_template('scholarships/3.html')


def get_scholarships_4():
    return render_template('scholarships/4.html')

