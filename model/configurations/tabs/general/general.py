#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######
from common.constants.view.configurations import general
from model.db import Db
import common.utility as utility

import json
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class General(Base):
    __tablename__ = "configuration_general"

    id = Column(Integer, primary_key=True)
    cases_folder_path = Column(String)
    home_page_url = Column(String)
    language = Column(String)
    user_agent = Column(String)

    def __init__(self) -> None:
        super().__init__()
        self.db = Db()
        self.metadata.create_all(self.db.engine)

    def get(self):
        if self.db.session.query(General).first() is None:
            self.set_default_values()

        return self.db.session.query(General).all()

    def update(self, configuration):
        self.db.session.query(General).filter(
            General.id == configuration.get("id")
        ).update(configuration)
        self.db.session.commit()

    def set_default_values(self):
        default_path_by_os = {
            "lin": "~/Documents/FIT",
            "osx": "~/Documents/FIT",
            "win": "~/Documents/FIT",
            "other": "~/Documents/FIT",
        }
        self.cases_folder_path = default_path_by_os[utility.get_platform()]
        self.home_page_url = "https://www.google.it"
        self.user_agent = general.DEFAULT_USER_AGENT
        self.language = "english"

        self.db.session.add(self)
        self.db.session.commit()
