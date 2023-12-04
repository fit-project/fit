#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######


from PyQt6.QtCore import QObject, pyqtSignal
from common.constants.view.tasks import status

from common.constants.view import video
from common.constants import error


class VideoLoadWorker(QObject):
    load_finished = pyqtSignal(str, object)
    error = pyqtSignal(object)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        self._options = options

    def load(self):
        url = self.options.get("url")
        controller = self.options.get("video_controller")
        info = {}
        __status = status.SUCCESS

        if controller.video_id is None:
            controller.set_url(url)
            try:
                if not controller.is_facebook_video():
                    controller.get_video_id(url)
                else:
                    controller.video_id = "facebook"
            except Exception as e:
                self.error.emit(
                    {
                        "title": video.INVALID_URL,
                        "msg": error.INVALID_URL,
                        "details": str(e),
                    }
                )
            else:
                try:
                    title, thumbnail, duration = controller.print_info()
                    is_youtube_video = controller.is_youtube_video()
                    audio_available = controller.is_audio_available()
                    availabe_resolution = controller.get_available_resolutions()
                    id_digest = controller.id_digest

                    info = {
                        "title": title,
                        "thumbnail": thumbnail,
                        "duration": duration,
                        "is_youtube_video": is_youtube_video,
                        "audio_available": audio_available,
                        "availabe_resolution": availabe_resolution,
                        "id_digest": id_digest,
                    }
                except Exception as e:
                    self.error.emit(
                        {
                            "title": video.SERVER_ERROR,
                            "msg": error.GENERIC_ERROR,
                            "details": str(e),
                        }
                    )

        self.load_finished.emit(__status, info)
