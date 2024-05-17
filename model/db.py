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

import os
import sys


class Db:
    def __init__(self) -> None:
        self._engine = create_engine(
            "sqlite:///" + self.__resolve_executable_path("fit.db"), echo=False
        )
        _Session = sessionmaker(bind=self._engine)
        self._session = _Session()

    @property
    def engine(self):
        return self._engine

    @property
    def session(self):
        return self._session

    def __resolve_executable_path(self, path):
        if getattr(sys, "frozen", False):

            if sys.platform == "win32":
                resolve_executable_path = os.path.abspath(
                    os.path.join(os.getcwd(), path)
                )
            elif sys.platform == "darwin":
                import macos_application_location

                resolve_executable_path = os.path.abspath(
                    os.path.join(str(macos_application_location.get().parent), path)
                )
            else:
                resolve_executable_path = os.path.abspath(
                    os.path.join(os.getcwd(), path)
                )
        else:
            # Normal development mode. Use os.getcwd() or __file__ as appropriate in your case...
            resolve_executable_path = os.path.abspath(os.path.join(os.getcwd(), path))

        return resolve_executable_path
