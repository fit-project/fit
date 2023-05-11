#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
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