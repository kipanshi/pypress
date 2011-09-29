#! /usr/bin/env python
#coding=utf-8
"""
    account.py
    ~~~~~~~~~~~~~
    :license: BSD, see LICENSE for more details.
"""

import datetime
import os, sys

# parse_qsl moved to urlparse module in v2.6
try:
  from urlparse import parse_qsl
except:
  from cgi import parse_qsl

import oauth2 as oauth

from flask import Blueprint, Response, request, flash, jsonify, g, current_app,\
    abort, redirect, url_for, session

from flaskext.babel import gettext as _
from flaskext.principal import identity_changed, Identity, AnonymousIdentity

from pypress.helpers import render_template, cached
from pypress.permissions import auth, admin
from pypress.extensions import db

from pypress.models import User, UserCode, Twitter
from pypress.forms import LoginForm, SignupForm

from pypress import twitter

account = Blueprint('account', __name__)

REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL  = 'https://api.twitter.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
SIGNIN_URL        = 'https://api.twitter.com/oauth/authenticate'

@account.route("/login/", methods=("GET","POST"))
def login():

    form = LoginForm(login=request.args.get('login',None),
                     next=request.args.get('next',None))

    if form.validate_on_submit():

        user, authenticated = User.query.authenticate(form.login.data,
                                                      form.password.data)

        if user and authenticated:
            session.permanent = form.remember.data

            identity_changed.send(current_app._get_current_object(),
                                  identity=Identity(user.id))

            flash(_("Welcome back, %(name)s", name=user.username), "success")

            next_url = form.next.data

            if not next_url or next_url == request.path:
                next_url = url_for('frontend.blog', username=user.username)

            return redirect(next_url)

        else:

            flash(_("Sorry, invalid login"), "error")

    return render_template("account/login.html", form=form)


@account.route("/signup/", methods=("GET","POST"))
def signup():

    form = SignupForm(next=request.args.get('next',None))

    if form.validate_on_submit():

        code = UserCode.query.filter_by(code=form.code.data).first()

        if code:
            user = User(role=code.role)
            form.populate_obj(user)

            db.session.add(user)
            db.session.delete(code)
            db.session.commit()

            identity_changed.send(current_app._get_current_object(),
                                  identity=Identity(user.id))

            flash(_("Welcome, %(name)s", name=user.nickname), "success")

            next_url = form.next.data

            if not next_url or next_url == request.path:
                next_url = url_for('frontend.blog', username=user.username)

            return redirect(next_url)
        else:
            form.code.errors.append(_("Code is not allowed"))

    return render_template("account/signup.html", form=form)

@account.route("/logout/")
def logout():

    flash(_("You are now logged out"), "success")
    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())

    next_url = request.args.get('next','')

    if not next_url or next_url == request.path:
        next_url = url_for("frontend.blog")

    return redirect(next_url)

