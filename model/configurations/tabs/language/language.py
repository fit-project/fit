#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from model.db import Db

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Language(Base):
    __tablename__ = 'configuration_language'

    id = Column(Integer, primary_key=True)
    language = Column(String)

    def __init__(self) -> None:
        super().__init__()
        self.db = Db()
        self.metadata.create_all(self.db.engine)

    def get(self):
        if self.db.session.query(Language).first() is None:
            self.set_default_values()

        return self.db.session.query(Language).all()

    def update(self, options):
        self.db.session.query(Language).filter(Language.id == options.get('id')).update(options)
        self.db.session.commit()

    def set_default_values(self):
        self.language = "Italian"

        self.db.session.add(self)
        self.db.session.commit()