#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PyQt6.QtCore import pyqtSignal, QThread
from PyQt6.QtWidgets import QMessageBox

from view.tasks.instagram.login import InstagramLoginWorker
from view.tasks.instagram.scraper import InstagramScrapeWorker
from view.tasks.task import Task
from view.error import Error as ErrorView

from controller.instagram import Instagram as InstragramController

from common.constants.view.tasks import labels, state, status
from common.constants import logger


class TaskInstagram(Task):
    logged_in = pyqtSignal(str, int)
    scraped = pyqtSignal()
    progress = pyqtSignal()

    def __init__(self, logger, progress_bar=None, status_bar=None, parent=None):
        super().__init__(logger, progress_bar, status_bar, parent)

        self.label = labels.INSTAGRAM_SCRAPER
        self.sub_task = None
        self.sub_task_thread = None
        self.sub_tasks = [
            {
                "label": labels.LOGGED_IN,
                "state": self.state,
                "status": self.status,
            },
            {
                "label": labels.SCRAPE_PROFILE,
                "state": self.state,
                "status": self.status,
            },
        ]

        self.destroyed.connect(lambda: self.__destroyed_handler(self.__dict__))

    def start(self):
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.INSTAGRAM_SCRAPER_STARTED)
        self.logger.info(logger.INSTAGRAM_SCRAPER_STARTED)
        self.options["instagram_controller"] = InstragramController()

        self.__started()

    def __started(self):
        self.update_task(state.STARTED, status.SUCCESS)
        self.started.emit()

    def login(self):
        self.sub_task = InstagramLoginWorker()
        self.sub_task_thread = QThread()
        self.sub_task.moveToThread(self.sub_task_thread)
        self.sub_task_thread.started.connect(self.sub_task.login)
        self.sub_task.logged_in.connect(self.__logged_in)
        self.sub_task.error.connect(self.__handle_error)
        self.sub_task.options = self.options

        self.sub_task_thread.start()

    def __logged_in(self, __status, __account_type):
        sub_task_logged_in = next(
            (task for task in self.sub_tasks if task.get("label") == labels.LOGGED_IN),
            None,
        )
        if sub_task_logged_in:
            sub_task_logged_in["state"] = state.COMPLETED
            sub_task_logged_in["status"] = __status

        self.logger.info(
            logger.INSTAGRAM_SCRAPER_LOGGED_IN.format(
                self.options["auth_info"].get("username"), __status
            )
        )
        self.set_message_on_the_statusbar(
            logger.INSTAGRAM_SCRAPER_LOGGED_IN.format(
                self.options["auth_info"].get("username"), __status
            )
        )

        self.logged_in.emit(__status, __account_type)

        self.__quit_to_sub_task()

    def scrape(self):
        self.sub_task = InstagramScrapeWorker()
        self.sub_task_thread = QThread()
        self.sub_task.moveToThread(self.sub_task_thread)
        self.sub_task_thread.started.connect(self.sub_task.scrape)
        self.sub_task.scraped.connect(self.__scrape_finished)
        self.sub_task.progress.connect(self.progress.emit)
        self.sub_task.error.connect(self.__handle_error)
        self.sub_task.options = self.options
        self.sub_task_thread.start()

    def __scrape_finished(self):
        sub_task_scrape = next(
            (
                task
                for task in self.sub_tasks
                if task.get("label") == labels.SCRAPE_PROFILE
            ),
            None,
        )
        if sub_task_scrape:
            sub_task_scrape["state"] = state.COMPLETED
            sub_task_scrape["status"] = status.SUCCESS

        self.logger.info(
            logger.INSTAGRAM_SCRAPER_SCRAPE.format(
                self.options["auth_info"].get("profile")
            )
        )
        self.set_message_on_the_statusbar(
            logger.INSTAGRAM_SCRAPER_SCRAPE.format(
                self.options["auth_info"].get("profile")
            )
        )

        self.scraped.emit()

        self.__quit_to_sub_task()
        self.__finished()

    def __finished(self):
        self.logger.info(logger.INSTAGRAM_SCRAPER_COMPLETED)
        self.set_message_on_the_statusbar(logger.INSTAGRAM_SCRAPER_COMPLETED)
        self.update_task(state.COMPLETED, status.SUCCESS)

        self.finished.emit()

    def __quit_to_sub_task(self):
        if self.sub_task_thread is not None:
            self.sub_task_thread.quit()
            self.sub_task_thread.wait()
            self.sub_task_thread = None
        if self.sub_task is not None:
            self.sub_task = None

    def __destroyed_handler(self, _dict):
        if self.sub_task_thread is not None and self.sub_task_thread.isRunning():
            self.sub_task_thread.quit()
            self.sub_task_thread.wait()

    def __handle_error(self, error):
        error_dlg = ErrorView(
            QMessageBox.Icon.Critical,
            error.get("title"),
            error.get("message"),
            error.get("details"),
        )
        error_dlg.exec()
