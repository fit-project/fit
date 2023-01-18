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
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()



class General(Base):

    __tablename__ = 'configuration_general'
    
    id = Column(Integer, primary_key = True)
    cases_folder_path = Column(String)
    home_page_url = Column(String)

    
    def __init__(self) -> None:
        super().__init__()
        self.db = Db()
        self.metadata.create_all(self.db.engine)
    

    def get(self):
        if self.db.session.query(General).first() is None:
            self.set_default_values()
            
        return self.db.session.query(General).all()
    
    def update(self, configuration):
        self.db.session.query(General).filter(General.id == configuration.get('id')).update(configuration)
        self.db.session.commit()
    
    def set_default_values(self):
        
        default_path_by_os = {"lin": "~/Documents/FIT", "osx": "~/Documents/FIT", "win": "~/Documents/FIT"}
        self.cases_folder_path = default_path_by_os[utility.get_platform()]
        self.home_page_url = "https://www.google.it"
        
        self.db.session.add(self)
        self.db.session.commit()