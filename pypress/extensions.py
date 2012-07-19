#!/usr/bin/env python
#coding=utf-8

from flask.ext.mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cache import Cache
from flask.ext.uploads import UploadSet, AllExcept, EXECUTABLES, SCRIPTS

__all__ = ['mail', 'db', 'cache', 'photos']

mail = Mail()
db = SQLAlchemy()
cache = Cache()
uploader = UploadSet('uploads', AllExcept(SCRIPTS + EXECUTABLES))

