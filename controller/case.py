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

from model.case import Case as CaseModel

from urllib.parse import urlparse

import common.utility as utility

class Case:
  _cases = []
  _names = []

  def __init__(self):
    self.model = CaseModel()
    _cases = self.model.get()
    self._keys = self.model.metadata.tables['cases'].columns.keys()

    for i in range(len(_cases)):
      self._cases.append({key: value for key, value in _cases[i].__dict__.items() if not key.startswith("_") and not key.startswith("__")})
      self._names.append({key: value for key, value in _cases[i].__dict__.items() if key == 'name'})
  
  @property
  def keys(self):
    return self._keys
    
  @property
  def cases(self):    
    return self._cases
  
  @cases.setter
  def cases(self, case_info):
    self.model.update(case_info)
  
  def add(self, case_info):
    case_info = self.model.add(case_info)
    
    return {key: value for key, value in case_info.__dict__.items() if not key.startswith("_") and not key.startswith("__")}
  
  @property
  def names(self):
     return list(map(lambda x : x['name'], self._names))

  def create_acquisition_directory(self, acquisition_type, cases_folder, case_folder, content):
        #Directories: Cases -> Case Name -> Acquisition Type -> Acquisiton Content
        if acquisition_type == 'web' :
            content = urlparse(content).netloc
            
        directories = { 'cases_folder': cases_folder,
                        'case_folder': case_folder,
                        'acquisition_type_folder' : acquisition_type,
                        'content_folder' :  content }

        return self.model.create_acquisition_directory(directories)



        