#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
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
        self.enabled = False

        self.db.session.add(self)
        self.db.session.commit()

