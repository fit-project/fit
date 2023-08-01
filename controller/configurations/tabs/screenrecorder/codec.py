#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from model.configurations.tabs.screenrecorder.codec import Codec as CodecModel


class Codec:
    _codec = []

    def __init__(self):
        self.model = CodecModel()
        _codec = self.model.get()
        if not len(self._codec):
            for i in range(len(_codec)):
                self._codec.append(
                    {
                        key: value
                        for key, value in _codec[i].__dict__.items()
                        if not key.startswith("_") and not key.startswith("__")
                    }
                )

    @property
    def codec(self):
        return self._codec
