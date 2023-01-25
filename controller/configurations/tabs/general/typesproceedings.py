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

from model.configurations.tabs.general.typesproceedings import TypesProceedings as TypesProceedingsModel

class TypesProceedings():
    _proceedings = []
    _names = []

    def __init__(self):
      self.model = TypesProceedingsModel()
      _proceedings = self.model.get()

      for i in range(len(_proceedings)):
        self._proceedings.append({key: value for key, value in _proceedings[i].__dict__.items() if not key.startswith("_") and not key.startswith("__")})
        self._names.append({key: value for key, value in _proceedings[i].__dict__.items() if key == 'name'})
    

    @property
    def proceedings(self):
      return self._proceedings
    
    @property
    def names(self):
      return list(map(lambda x : x['name'], self._names))
    
    @names.setter
    def names(self, names):
      names_to_delete = [item for item in list(map(lambda x : x['name'], self._names)) if item not in names]
      if names_to_delete:
        ids = []
        for proceedings in self._proceedings:
            if proceedings['name'] in names_to_delete:
              ids.append(proceedings['id'])

        self.model.delete(ids)


      names_to_add = [item for item in names if item not in list(map(lambda x : x['name'], self._names))]
      if names_to_add:
        self.model.add(names_to_add)
