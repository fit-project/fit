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
import common.utility as utility

import json
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()



class Network(Base):

    __tablename__ = 'configuration_network'
    
    id = Column(Integer, primary_key = True)
    ntp_server = Column(String)
    nslookup_dns_server = Column(String)
    nslookup_enable_tcp = Column(Boolean)
    nslookup_enable_verbose_mode = Column(Boolean)
    
    def __init__(self) -> None:
        super().__init__()
        self.db = Db()
        self.metadata.create_all(self.db.engine)
    

    def get(self):
        if self.db.session.query(Network).first() is None:
            self.set_default_values()
            
        return self.db.session.query(Network).all()
    
    def update(self, configuration):
        self.db.session.query(Network).filter(Network.id == configuration.get('id')).update(configuration)
        self.db.session.commit()
    
    def set_default_values(self):
        
        self.ntp_server = "ntp1.inrim.it"
        self.nslookup_dns_server = "1.1.1.1"
        self.nslookup_enable_tcp = False
        self.nslookup_enable_verbose_mode = False
        
        self.db.session.add(self)
        self.db.session.commit()