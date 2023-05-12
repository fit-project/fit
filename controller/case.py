#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
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
    
    return {key: value for key, value in case_info.__dict__.items() if not key.startswith("_") and not key.startswith("__") and not key.startswith("db")}
  
  @property
  def names(self):
     return list(map(lambda x : x['name'], self._names))

  def create_acquisition_directory(self, acquisition_type, cases_folder, case_folder, content):
        #Directories: Cases -> Case Name -> Acquisition Type -> Acquisition Content
        if acquisition_type == 'web' :
            content = urlparse(content).netloc
            
        directories = { 'cases_folder': cases_folder,
                        'case_folder': case_folder,
                        'acquisition_type_folder' : acquisition_type,
                        'content_folder' :  content }

        return self.model.create_acquisition_directory(directories)



        