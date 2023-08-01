#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Db:
    def __init__(self) -> None:
        self._engine = create_engine("sqlite:///fit.db", echo=False)
        _Session = sessionmaker(bind=self._engine)
        self._session = _Session()

    @property
    def engine(self):
        return self._engine

    @property
    def session(self):
        return self._session
