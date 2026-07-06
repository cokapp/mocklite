#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File   : manage.py
# @Author : mocobk
# @Email  : mailmzb@qq.com
# @Time   : 2020/1/8 14:27
from app import create_app
from app.extensions import db
from config import BANNER

app = create_app()
with app.app_context():
    db.create_all()

print(BANNER)
