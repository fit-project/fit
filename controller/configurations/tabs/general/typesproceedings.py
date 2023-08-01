#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from model.configurations.tabs.general.typesproceedings import (
    TypesProceedings as TypesProceedingsModel,
)


class TypesProceedings:
    _proceedings = []
    _names = []

    def __init__(self):
        self.model = TypesProceedingsModel()

        _proceedings = self.model.get()

        if not len(self._proceedings):
            for i in range(len(_proceedings)):
                self._proceedings.append(
                    {
                        key: value
                        for key, value in _proceedings[i].__dict__.items()
                        if not key.startswith("_")
                        and not key.startswith("__")
                        and not key.startswith("db")
                    }
                )
                self._names.append(
                    {
                        key: value
                        for key, value in _proceedings[i].__dict__.items()
                        if key == "name"
                    }
                )

    @property
    def proceedings(self):
        return self._proceedings

    @property
    def names(self):
        return list(map(lambda x: x["name"], self._names))

    @names.setter
    def names(self, names):
        names_to_delete = [
            item
            for item in list(map(lambda x: x["name"], self._names))
            if item not in names
        ]
        if names_to_delete:
            ids = []
            for proceedings in self._proceedings:
                if proceedings["name"] in names_to_delete:
                    ids.append(proceedings["id"])

            self.model.delete(ids)

        names_to_add = [
            item
            for item in names
            if item not in list(map(lambda x: x["name"], self._names))
        ]
        if names_to_add:
            self.model.add(names_to_add)
