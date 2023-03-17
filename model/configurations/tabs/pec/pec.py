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

    pec = Column(String, primary_key=True)
    password = Column(String)
    server = Column(String)
    port = Column(String)
    serverImap = Column(String)
    portImap = Column(String)

    def __init__(self) -> None:
        super().__init__()
        self.db = Db()
        self.metadata.create_all(self.db.engine)

    def delete(self, pecData):
        return self.db.session.query(Pec).filter(Pec.pec == pecData).delete()

    def get(self):
        return self.db.session.query(Pec).all()

    def close(self):
        self.db.session.close_all()
        return

    def update(self, pecData, passwordData, serverData, portData, serverImapData, portImapData):
        self.db.session.query(Pec).filter(Pec.pec == pecData).update(pecData, passwordData, serverData, portData,
                                                                     serverImapData, portImapData)
        self.db.session.commit()

    def add(self, pecData, passwordData, serverData, portData, serverImapData, portImapData):
        self.pec = pecData
        self.password = passwordData
        self.server = serverData
        self.port = portData
        self.serverImap = serverImapData
        self.portImap = portImapData

        self.db.session.add(self)
        self.db.session.commit()

        return self.db.session.query(Pec)


