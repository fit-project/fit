#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from enum import Enum, auto
from PyQt6 import QtCore, QtWidgets, uic


from PyQt6.QtMultimedia import (
    QMediaCaptureSession,
    QScreenCapture,
    QWindowCapture,
)

from view.error import Error as ErrorView
from view.dialog import Dialog, DialogButtonTypes


from view.configurations.screen_recorder_preview.screen_list_model import (
    ScreenListModel,
)

from view.configurations.screen_recorder_preview.window_list_model import (
    WindowListModel,
)

from common.utility import resolve_path, get_version

from common.constants.view.screenrecorder import *

from ui.configuration import resources


class SourceType(Enum):
    SCREEN = auto()
    WINDOW = auto()


__is_tab__ = False


class ScreenRecorderPreview(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ScreenRecorderPreview, self).__init__(parent)
        self.__init_ui()

    def __init_ui(self):
        uic.loadUi(
            resolve_path("ui/screen_recorder_preview/screen_recorder_preview.ui"), self
        )

        # HIDE STANDARD TITLE BAR
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        # CUSTOM TOP BAR
        self.left_box.mouseMoveEvent = self.move_window

        # MINIMIZE BUTTON
        self.minimize_button.clicked.connect(self.showMinimized)

        # CLOSE BUTTON
        self.close_button.clicked.connect(self.close)

        # SET VERSION
        self.version.setText("v" + get_version())

        app = QtWidgets.QApplication.instance()
        if not hasattr(app, "screen_information"):
            screen_information = {
                "source_type": SourceType.SCREEN,
                "screen_to_record": app.primaryScreen(),
            }

            setattr(app, "screen_information", screen_information)

        self.__screen_information = getattr(app, "screen_information")
        self.__screen_to_record = self.__screen_information.get("screen_to_record")
        __initial_source_type = self.__screen_information.get("source_type")

        # SET SCREEN RECORDER LIST VIEW
        self._screen_list_model = ScreenListModel(self)

        if __initial_source_type == SourceType.SCREEN:
            w = self.__screen_to_record.size().width()
            h = self.__screen_to_record.size().height()
            dpi = self.__screen_to_record.logicalDotsPerInch()
            key_word = f'"{self.__screen_to_record.name()}" {w}x{h}, {dpi}DPI'

            indexes = self._screen_list_model.match(
                self._screen_list_model.index(0, 0),
                QtCore.Qt.ItemDataRole.DisplayRole,
                key_word,
                1,
                QtCore.Qt.MatchFlag.MatchRecursive,
            )

            if len(indexes):
                self._screen_list_model.setData(
                    indexes[0], 2, QtCore.Qt.ItemDataRole.CheckStateRole
                )

        self.screen_recorder_list_view.setModel(self._screen_list_model)

        self._screen_list_model.dataChanged.connect(
            self.on_current_screen_selection_changed
        )

        # SET WINDOW RECORDER LIST VIEW
        self._window_list_model = WindowListModel(self)
        if __initial_source_type == SourceType.WINDOW:

            if not self.__screen_to_record.isValid():
                self.__not_valid_window_dialog()
                # SET FIRST WINDOW OF LIST
                self.__screen_to_record = self._window_list_model.window(
                    self._window_list_model.index(0, 0)
                )

            key_word = self.__screen_to_record.description()

            indexes = self._window_list_model.match(
                self._window_list_model.index(0, 0),
                QtCore.Qt.ItemDataRole.DisplayRole,
                key_word,
                1,
                QtCore.Qt.MatchFlag.MatchRecursive,
            )

            if len(indexes):
                self._window_list_model.setData(
                    indexes[0], 2, QtCore.Qt.ItemDataRole.CheckStateRole
                )

        self.window_recorder_list_view.setModel(self._window_list_model)

        self._window_list_model.dataChanged.connect(
            self.on_current_window_selection_changed
        )

        self._screen_capture = QScreenCapture(self)
        self._media_capture_session = QMediaCaptureSession(self)

        # SETUP SCREEN CAPTURE WITH INITIAL SOURCE:
        if __initial_source_type == SourceType.SCREEN:
            self.setScreen(self.__screen_to_record)
        else:
            self.setScreen(QtWidgets.QApplication.primaryScreen())

        self._screen_capture.start()
        self._media_capture_session.setScreenCapture(self._screen_capture)
        self._media_capture_session.setVideoOutput(self.video_output)

        # SETUP WINDOW CAPTURE WITH INITIAL SOURCE:
        self._window_capture = QWindowCapture(self)
        if __initial_source_type == SourceType.WINDOW:
            self._window_capture.setWindow(self.__screen_to_record)

        self._media_capture_session.setWindowCapture(self._window_capture)

        self._screen_capture.errorOccurred.connect(
            self.on_screen_capture_error_occured,
            QtCore.Qt.ConnectionType.QueuedConnection,
        )
        self._window_capture.errorOccurred.connect(
            self.on_window_capture_error_occured,
            QtCore.Qt.ConnectionType.QueuedConnection,
        )
        self.update_active(__initial_source_type, True)

    def on_current_screen_selection_changed(self, index):
        self._window_list_model.populate()
        self.__screen_to_record = self._screen_list_model.screen(index)
        self._screen_capture.setScreen(self.__screen_to_record)
        self.update_active(SourceType.SCREEN, self.is_active())
        self.window_recorder_list_view.clearSelection()

    def on_current_window_selection_changed(self, index):
        self._screen_list_model.screens_changed()
        window = self._window_list_model.window(index)
        if not window.isValid():
            self.__not_valid_window_dialog()
        else:
            self.__screen_to_record = window
            self._window_capture.setWindow(window)
            self.update_active(SourceType.WINDOW, self.is_active())
            self.window_recorder_list_view.clearSelection()

    def __not_valid_window_dialog(self):
        dialog = Dialog(
            PREVIEW_ERROR_NOT_VALID_WINDOW_TITLE,
            PREVIEW_ERROR_NOT_VALID_WINDOW_MSG,
        )
        dialog.message.setStyleSheet("font-size: 13px;")
        dialog.set_buttons_type(DialogButtonTypes.MESSAGE)
        dialog.right_button.clicked.connect(lambda: self.__update_window_list(dialog))

        dialog.content_box.adjustSize()

        dialog.exec()

    def __update_window_list(self, dialog=None):
        if dialog:
            dialog.close()

        self.window_recorder_list_view.clearSelection()
        self._window_list_model.populate()

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    def move_window(self, event):
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
            self.dragPos = event.globalPosition().toPoint()
            event.accept()

    def accept(self):
        return super().accept()

    def reject(self):
        return super().reject()

    @QtCore.pyqtSlot(QWindowCapture.Error, str)
    def on_window_capture_error_occured(self, error, error_string):
        error_dlg = ErrorView(
            QtWidgets.QMessageBox.Icon.Critical,
            PREVIEW_WINDOW_CAPTURE_ERROR_OCCURED_TITLE,
            error_string,
            str(error),
        )
        error_dlg.exec()

    @QtCore.pyqtSlot(QScreenCapture.Error, str)
    def on_screen_capture_error_occured(self, error, error_string):
        error_dlg = ErrorView(
            QtWidgets.QMessageBox.Icon.Critical,
            PREVIEW_SCREEN_CAPTURE_ERROR_OCCURED_TITLE,
            error_string,
            str(error),
        )
        error_dlg.exec()

    def update_active(self, source_type, active):
        self._source_type = source_type
        self._screen_capture.setActive(active and source_type == SourceType.SCREEN)
        self._window_capture.setActive(active and source_type == SourceType.WINDOW)

        self.__screen_information["source_type"] = source_type
        self.__screen_information["screen_to_record"] = self.__screen_to_record

    def is_active(self):
        if self._source_type == SourceType.WINDOW:
            return self._window_capture.isActive()
        if self._source_type == SourceType.SCREEN:
            return self._screen_capture.isActive()
        return False
