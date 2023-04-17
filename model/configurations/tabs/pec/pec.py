#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# MIT License
#
# Copyright (c) 2022 FIT-Project and others
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----
######

from model.db import Db
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Pec(Base):
    __tablename__ = 'configuration_pec'
    id = Column(Integer, primary_key = True)
    enabled = Column(Boolean)
    pec_email = Column(String)
    password = Column(String)
    smtp_server = Column(String)
    smtp_port = Column(String)
    imap_server = Column(String)
    imap_port = Column(String)
    retries = Column(Integer)

    def __init__(self) -> None:
        super().__init__()
        self.db = Db()
        self.metadata.create_all(self.db.engine)

    def get(self):
        if self.db.session.query(Pec).first() is None:
            self.set_default_values()
        return self.db.session.query(Pec).all()
   

    def update(self, options):
        self.db.session.query(Pec).filter(Pec.id == options.get('id')).update(options)
        self.db.session.commit()
    
    def set_default_values(self):
        self.pec_email = ""
        self.password = ""
        self.smtp_server = ""
        self.smtp_port = ""
        self.imap_server = ""
        self.imap_port = ""
        self.retries = 5
        self.enabled = True

        self.db.session.add(self)
        self.db.session.commit()

