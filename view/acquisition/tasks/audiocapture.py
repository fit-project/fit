#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import wave

import pyaudio as pa
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot


class RecordingThread(QThread):
    stopped = False
    sig_started = pyqtSignal()
    sig_stopped = pyqtSignal()

    def __init__(self, target_file):
        self.target_file = target_file
        super().__init__()

    def run(self) -> None:
        audio = pa.PyAudio()
        frames = []
        stream = audio.open(
            format=pa.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024,
        )
        self.stopped = False
        self.sig_started.emit()

        while not self.stopped:
            data = stream.read(1024)
            frames.append(data)

        stream.close()

        self.sig_stopped.emit()

        wf = wave.open(self.target_file, "wb")
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pa.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b"".join(frames))
        wf.close()

    @pyqtSlot()
    def stop(self):
        self.stopped = True
