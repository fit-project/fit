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

from view.tasks.entire_website.url import EntireWebsiteUrlWorker
from view.tasks.entire_website.sitemap import EntireWebsiteSitemapWorker
from view.tasks.entire_website.download import EntireWebsiteDownloadWorker
from view.tasks.task import Task
from view.error import Error as ErrorView

from controller.entire_website import EntireWebsite as EntireWebsiteController

from common.constants.view.tasks import labels, state, status
from common.constants import logger


class TaskEntireWebsite(Task):
    valid_url = pyqtSignal(str)
    sitemap_finished = pyqtSignal(str, set)
    download_finished = pyqtSignal()
    progress = pyqtSignal()

    def __init__(self, logger, progress_bar=None, status_bar=None, parent=None):
        super().__init__(logger, progress_bar, status_bar, parent)

        self.label = labels.ENTIRE_WEBSITE_SCRAPER
        self.sub_task = None
        self.sub_task_thread = None
        self.sub_tasks = [
            {
                "label": labels.CHECK_IS_VALID_URL,
                "state": self.state,
                "status": self.status,
            },
            {
                "label": labels.GET_SITEMAP,
                "state": self.state,
                "status": self.status,
            },
            {
                "label": labels.DOWNLOAD_URLS,
                "state": self.state,
                "status": self.status,
            },
        ]

        self.destroyed.connect(lambda: self.__destroyed_handler(self.__dict__))

    def start(self):
        self.update_task(state.STARTED, status.PENDING)
        self.set_message_on_the_statusbar(logger.ENTIRE_WEBSITE_SCRAPER_STARTED)
        self.logger.info(logger.ENTIRE_WEBSITE_SCRAPER_STARTED)
        self.options["entire_website_controller"] = EntireWebsiteController()

        self.__started()

    def __started(self):
        self.update_task(state.STARTED, status.SUCCESS)
        self.started.emit()

    def check_is_valid_url(self, url):
        self.sub_task = EntireWebsiteUrlWorker()
        self.sub_task_thread = QThread()
        self.sub_task.moveToThread(self.sub_task_thread)
        self.sub_task_thread.started.connect(self.sub_task.check)
        self.sub_task.valid_url.connect(self.__is_valid_url)
        self.sub_task.error.connect(self.__handle_error)
        self.sub_task.options = self.options
        self.sub_task.options["url"] = url

        self.sub_task_thread.start()

    def __is_valid_url(self, __status):
        sub_task_valid_url = next(
            (
                task
                for task in self.sub_tasks
                if task.get("label") == labels.CHECK_IS_VALID_URL
            ),
            None,
        )
        if sub_task_valid_url:
            sub_task_valid_url["state"] = state.COMPLETED
            sub_task_valid_url["status"] = __status

        self.logger.info(
            logger.ENTIRE_WEBSITE_SCRAPER_CHECK_IS_VALID_URL.format(
                self.sub_task.options.get("url"), __status
            )
        )
        self.set_message_on_the_statusbar(
            logger.ENTIRE_WEBSITE_SCRAPER_CHECK_IS_VALID_URL_FININISHED.format(__status)
        )

        self.__quit_to_sub_task()

        self.valid_url.emit(__status)

    def get_sitemap(self):
        self.sub_task = EntireWebsiteSitemapWorker()
        self.sub_task_thread = QThread()
        self.sub_task.moveToThread(self.sub_task_thread)
        self.sub_task_thread.started.connect(self.sub_task.get_sitemap)
        self.sub_task.sitemap.connect(self.__get_sitemap_finished)
        self.sub_task.error.connect(self.__handle_error)
        self.sub_task.options = self.options
        self.sub_task_thread.start()

    def __get_sitemap_finished(self, __status, urls):
        sub_task_get_sitemap = next(
            (
                task
                for task in self.sub_tasks
                if task.get("label") == labels.GET_SITEMAP
            ),
            None,
        )
        if sub_task_get_sitemap:
            sub_task_get_sitemap["state"] = state.COMPLETED
            sub_task_get_sitemap["status"] = __status

        self.logger.info(logger.ENTIRE_WEBSITE_SCRAPER_URLS.format(__status))
        self.set_message_on_the_statusbar(
            logger.ENTIRE_WEBSITE_SCRAPER_URLS.format(__status)
        )

        self.sitemap_finished.emit(__status, urls)

        self.__quit_to_sub_task()

    def download_urls(self):
        self.sub_task = EntireWebsiteDownloadWorker()
        self.sub_task_thread = QThread()
        self.sub_task.moveToThread(self.sub_task_thread)
        self.sub_task_thread.started.connect(self.sub_task.download)
        self.sub_task.download_finished.connect(self.__download_finished)
        self.sub_task.progress.connect(self.progress.emit)
        self.sub_task.error.connect(self.__handle_error)
        self.sub_task.options = self.options
        self.sub_task_thread.start()

    def __download_finished(self, urls):
        sub_task_download = next(
            (
                task
                for task in self.sub_tasks
                if task.get("label") == labels.DOWNLOAD_URLS
            ),
            None,
        )
        if sub_task_download:
            sub_task_download["state"] = state.COMPLETED
            sub_task_download["status"] = status.SUCCESS

        for url in urls:
            self.logger.info(logger.DOWNLOADED.format(url))

        self.download_finished.emit()

        self.__quit_to_sub_task()
        self.__finished()

    def __finished(self):
        self.logger.info(
            logger.ENTIRE_WEBSITE_SCRAPER_DOWNLOADED.format(
                self.options.get("start_url")
            )
        )
        self.set_message_on_the_statusbar(logger.ENTIRE_WEBSITE_DOWNLOAD_FININISHED)
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
