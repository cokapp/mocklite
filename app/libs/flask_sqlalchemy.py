#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File   : query.py
# @Author : mocobk
# @Email  : mailmzb@qq.com
# @Time   : 2020/1/8 17:16
from contextlib import contextmanager

from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy
from flask_sqlalchemy.query import Query as _Query
from flask_sqlalchemy.session import Session as _Session

from app.libs.response import NotFound


class Query(_Query):
    def get_or_404(self, ident, description=None):
        rv = self.get(ident)
        if not rv:
            raise NotFound(message=description)
        return rv

    def first_or_404(self, description=None):
        rv = self.first()
        if not rv:
            raise NotFound(message=description)
        return rv


class QueryType(Query):
    """Just for Type Hint"""
    def filter(self, *criterion) -> Query:
        pass

    def filter_by(self, **kwargs) -> 'QueryType':
        pass

class SessionType(_Session):
    """Just for Type Hint"""
    def query(self, *entities, **kwargs) -> QueryType:
        pass

class SQLAlchemy(_SQLAlchemy):
    session: SessionType  # Just for Type Hint

    @contextmanager
    def auto_commit(self):
        """通过 with db.auto_commit() 管理上下文，失败自动回滚"""
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
