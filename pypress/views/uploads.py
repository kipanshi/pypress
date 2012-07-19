#! /usr/bin/env python
#coding=utf-8
"""
    views: link.py
    ~~~~~~~~~~~~~
    :license: BSD, see LICENSE for more details.
"""

from flask import Blueprint, Response, request, flash, jsonify, g, current_app,\
    abort, redirect, url_for, session

from flask.ext.babel import gettext as _

from pypress.helpers import render_template, cached
from pypress.permissions import auth, admin
from pypress.extensions import db, uploader

from pypress.models import Upload
from pypress.forms import UploadForm

uploads = Blueprint('uploads', __name__)

@uploads.route("/")
@uploads.route("/p/<int:page>/")
def index(page=1):
    if page < 1:
        page = 1
    ups = Upload.query

    page_obj = ups.paginate(page=page, per_page=Upload.PER_PAGE)

    page_url = lambda page: url_for("uploads.index",page=page)

    return render_template("blog/uploads.html",
                            page_obj=page_obj,
                            page_url=page_url)


@uploads.route("/add/", methods=("GET","POST"))
def add():

    form = UploadForm()

    if 'file' in request.files:

            filename = uploader.save(request.files['file'])
            upload = Upload(file=filename)
            db.session.add(upload)
            db.session.commit()

            flash(_("Upload successful"), "success")

            return redirect(url_for('uploads.index'))

    return render_template("blog/add_upload.html", form=form)


@uploads.route("/<int:upload_id>/delete/", methods=("POST",))
@auth.require(401)
def delete(upload_id):

    upload = Upload.query.get_or_404(upload_id)
    upload.permissions.delete.test(403)
    # DELETE THE FSCKING FILE!
    db.session.delete(upload)
    db.session.commit()

    return jsonify(success=True,
                   upload_id=upload_id)


