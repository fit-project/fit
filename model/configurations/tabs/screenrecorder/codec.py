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


class Codec(Base):
    __tablename__ = "configuration_codec"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self) -> None:
        super().__init__()
        self.db = Db()
        self.metadata.create_all(self.db.engine)

    def get(self):
        if self.db.session.query(Codec).first() is None:
            self.set_default_values()

        return self.db.session.query(Codec).all()

    def set_default_values(self):
        rows = []
        for name in ["XVID"]:
            if name:
                codec = Codec()
                codec.name = name.strip()
                rows.append(codec)

        self.db.session.add_all(rows)
        self.db.session.commit()
