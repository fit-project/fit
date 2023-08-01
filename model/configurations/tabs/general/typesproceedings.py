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


class TypesProceedings(Base):
    __tablename__ = "configuration_type_proceedings"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self) -> None:
        super().__init__()
        self.db = Db()
        self.metadata.create_all(self.db.engine)

    def get(self):
        if self.db.session.query(TypesProceedings).first() is None:
            self.set_default_values()

        return self.db.session.query(TypesProceedings).all()

    def add(self, names):
        rows = []
        for name in names:
            if name:
                proceedings = TypesProceedings()
                proceedings.name = name.strip()
                rows.append(proceedings)

        self.db.session.add_all(rows)
        self.db.session.commit()

    def delete(self, ids):
        if ids:
            self.db.session.query(TypesProceedings).filter(
                TypesProceedings.id.in_(ids)
            ).delete(synchronize_session=False)
            self.db.session.commit()

    def set_default_values(self):
        self.add(["Penale", "Civile", "Extragiudiziale"])
