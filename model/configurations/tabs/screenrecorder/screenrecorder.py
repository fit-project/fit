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


class ScreenRecorder(Base):
    __tablename__ = "configuration_screenrecorder"

    id = Column(Integer, primary_key=True)
    enabled = Column(Boolean)
    codec_id = Column(Integer)
    fps = Column(Integer)
    filename = Column(String)

    def __init__(self) -> None:
        super().__init__()
        self.db = Db()
        self.metadata.create_all(self.db.engine)

    def get(self):
        if self.db.session.query(ScreenRecorder).first() is None:
            self.set_default_values()

        return self.db.session.query(ScreenRecorder).all()

    def update(self, options):
        self.db.session.query(ScreenRecorder).filter(
            ScreenRecorder.id == options.get("id")
        ).update(options)
        self.db.session.commit()

    def set_default_values(self):
        self.enabled = True
        self.codec_id = 1
        self.fps = 25
        self.filename = "acquisition_video"

        self.db.session.add(self)
        self.db.session.commit()
