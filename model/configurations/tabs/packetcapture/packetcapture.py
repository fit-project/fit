#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######  

from model.db import Db

from sqlalchemy import  Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class PacketCapture(Base):

    __tablename__ = 'configuration_packetcapture'
    
    id = Column(Integer, primary_key = True)
    enabled = Column(Boolean)
    filename = Column(String)
    
    def __init__(self) -> None:
        super().__init__()
        self.db = Db()
        self.metadata.create_all(self.db.engine)
    
    def get(self):
        if self.db.session.query(PacketCapture).first() is None:
            self.set_default_values()
            
        return self.db.session.query(PacketCapture).all()
    
    def update(self, options):
        self.db.session.query(PacketCapture).filter(PacketCapture.id == options.get('id')).update(options)
        self.db.session.commit()
    
    def set_default_values(self):
        
        self.enabled = True
        self.filename = "acquisition.pcap"
        
        self.db.session.add(self)
        self.db.session.commit()