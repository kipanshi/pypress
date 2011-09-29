#! /usr/bin/env python
#coding=utf-8
"""
    feeds.py
    ~~~~~~~~~~~~~
    :license: BSD, see LICENSE for more details.
"""

import datetime
import os

from werkzeug.contrib.atom import AtomFeed

from flask import Blueprint, request, url_for

from pypress.helpers import cached

from pypress.models import User, Post, Tag

feeds = Blueprint('feeds', __name__)

class PostFeed(AtomFeed):

    def add_post(self, post):

        self.add(post.title,
                 unicode(post.summary),
                 content_type="html",
                 author=post.author.username,
                 url=post.permalink,
                 updated=post.update_time,
                 published=post.created_date)


@feeds.route("/")
@cached()
def index():
    feed = PostFeed("silverymoon - latest",
                    feed_url=request.url,
                    url=request.url_root)

    posts = Post.query.filter(Post._page == False).order_by('created_date desc').limit(15)

    for post in posts:
        feed.add_post(post)

    return feed.get_response()


@feeds.route("/tag/<slug>/")
@cached()
def tag(slug):

    tag = Tag.query.filter_by(slug=slug).first_or_404()

    feed = PostFeed("silverymoon - %s"  % tag,
                    feed_url=request.url,
                    url=request.url_root)

    posts = tag.posts.limit(15)

    for post in posts:
        feed.add_post(post)

    return feed.get_response()


