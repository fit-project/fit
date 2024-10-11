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
import sys, os


class Db:
    def __init__(self) -> None:
        self._engine = create_engine(
            "sqlite:///" + self.__resolve_db_path("fit.db"), echo=False
        )
        _Session = sessionmaker(bind=self._engine)
        self._session = _Session()

    @property
    def engine(self):
        return self._engine

    @property
    def session(self):
        return self._session

    def __resolve_db_path(self, path):
        if getattr(sys, "frozen", False):
            if sys.platform == "win32":
                local_path = os.path.join(os.path.expanduser("~"), "AppData", "Local")
            elif sys.platform == "darwin":
                local_path = os.path.expanduser("~/Library/Application Support")
            else:
                local_path = os.path.expanduser("~/.local/share")

            resolve_db_path = os.path.join(local_path, path)
        else:
            resolve_db_path = os.path.abspath(os.path.join(os.getcwd(), path))

        return resolve_db_path
