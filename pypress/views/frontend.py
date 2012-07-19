#! /usr/bin/env python
#coding=utf-8
"""
    frontend.py
    ~~~~~~~~~~~~~
    :license: BSD, see LICENSE for more details.
"""

import datetime
import os

from flask import Blueprint, Response, request, flash, jsonify, g, current_app,\
    abort, redirect, url_for, session, send_file, send_from_directory

from flask.ext.babel import gettext as _

from pypress.helpers import render_template, cached
from pypress.permissions import auth, admin
from pypress.extensions import db

from pypress.models import User, Post, Comment, Tag
from pypress.forms import CommentForm, TemplateForm, TwitterForm

frontend = Blueprint("frontend", __name__, static_folder='static')

@frontend.route("/p/<int:page>/")
@frontend.route("/<int:year>/")
@frontend.route("/<int:year>/p/<int:page>/")
@frontend.route("/<int:year>/<int:month>/")
@frontend.route("/<int:year>/<int:month>/p/<int:page>/")
@frontend.route("/<int:year>/<int:month>/<int:day>/")
@frontend.route("/<int:year>/<int:month>/<int:day>/p/<int:page>/")
def index(year=None, month=None, day=None, page=1):

    if page<1:page=1

    page_obj = Post.query.archive(year,month,day).as_list() \
                         .paginate(page, per_page=Post.PER_PAGE)

    page_url = lambda page: url_for("frontend.index",
                                    year=year,
                                    month=month,
                                    day=day,
                                    page=page)

    return render_template("blog/list.html",
                            page_obj=page_obj,
                            page_url=page_url)


@frontend.route("/search/")
@frontend.route("/search/p/<int:page>/")
def search(page=1):

    keywords = request.args.get('q','').strip()

    if not keywords:
        return redirect(url_for("frontend.blog"))

    page_obj = Post.query.search(keywords).as_list() \
                         .paginate(page, per_page=Post.PER_PAGE)

    if page_obj.total == 1:

        post = page_obj.items[0]
        return redirect(post.url)

    page_url = lambda page: url_for('frontend.search',
                                    page=page,
                                    keywords=keywords)

    return render_template("blog/search_result.html",
                           page_obj=page_obj,
                           page_url=page_url,
                           keywords=keywords)


@frontend.route("/archive/")
def archive():
    return render_template("blog/archive.html")


@frontend.route("/tags/")
def tags():

    return render_template("blog/tags.html")


@frontend.route("/tags/<slug>/")
@frontend.route("/tags/<slug>/p/<int:page>/")
def tag(slug, page=1):

    tag = Tag.query.filter_by(slug=slug).first_or_404()

    page_obj = tag.posts.as_list() \
                        .paginate(page, per_page=Post.PER_PAGE)

    page_url = lambda page: url_for("post.tag",
                                    slug=slug,
                                    page=page)

    return render_template("blog/list.html",
                            page_obj=page_obj,
                            page_url=page_url)



@frontend.route("/blog/")
def blog():
    return index()

@frontend.route("/")
def start():
    return display(u'index')

@frontend.route("/page/<slug>")
def display(slug):
    post = Post.query.get_by_slug(slug)
    return render_template("blog/page.html", post=post)

@frontend.route("/<int:year>/<int:month>/<int:day>/<slug>/")
def post(year, month, day, slug):

    post = Post.query.get_by_slug(slug)

    date = (post.created_date.year,
            post.created_date.month,
            post.created_date.day)

    if date != (year, month, day):
        return redirect(post.url)

    prev_post = Post.query.filter(Post.created_date<post.created_date) \
                          .first()
    next_post = Post.query.filter(Post.created_date>post.created_date) \
                          .order_by('created_date asc').first()

    return render_template("blog/view.html",
                            post=post,
                            prev_post=prev_post,
                            next_post=next_post,
                            comment_form=CommentForm())


@frontend.route("/<slug>/")
@frontend.route("/<path:date>/<slug>/")
def _post(slug, date=None):

    post = Post.query.get_by_slug(slug)

    return redirect(post.url)

