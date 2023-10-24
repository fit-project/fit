import os
import sys
import unittest

import logging

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QSignalSpy


from view.acquisition.acquisition import Acquisition
from view.tasks.info import TasksInfo
from view.tasks.nettools.sslkeylog import TaskSSLKeyLog

from common.utility import resolve_path
from common.constants import state, status, tasks, logger as Logger

from tests.tasks.tasks_ui import Ui_MainWindow

app = QApplication(sys.argv)

logger = logging.getLogger("view.web.web")


class TaskSSLKeyLogTest(unittest.TestCase):
    folder = ""
    acquisition = None
    tasks_info = None
    window = None
    increment = 0

    @classmethod
    def setUpClass(cls):
        options = {"acquisition_directory": cls.folder}
        cls.task = TaskSSLKeyLog(
            options,
            cls.acquisition.logger,
            cls.tasks_info,
            cls.window.progressBar,
            cls.window.statusbar,
        )

        cls.intial_progress_bar_value = cls.window.progressBar.value()
        cls.task.increment = cls.increment

    def test_00_init_headers_task(self):
        self.assertEqual(self.task.name, tasks.SSLKEYLOG)
        self.assertEqual(self.task.state, state.INITIALIZATED)
        self.assertEqual(self.task.status, status.DONE)
        self.assertEqual(self.task.progress_bar.value(), 0)

        row = self.tasks_info.get_row(tasks.SSLKEYLOG)
        if row >= 0:
            self.assertEqual(
                self.task.state,
                self.tasks_info.table.item(row, 1).text(),
            )
            self.assertEqual(
                self.task.status,
                self.tasks_info.table.item(row, 2).text(),
            )

    def test_01_headers_task(self):
        spy = QSignalSpy(self.task.started)

        self.task.start()

        if len(spy) == 0:
            received = spy.wait(500)
            while received is False:
                received = spy.wait(500)

        self.assertEqual(len(spy), 1)

        self.assertEqual(
            self.task.status_bar.currentMessage(),
            Logger.SSLKEYLOG_STARTED,
        )
        self.assertEqual(self.task.progress_bar.value(), 0)

        spy = QSignalSpy(self.task.finished)

        if len(spy) == 0:
            received = spy.wait(500)
            while received is False:
                received = spy.wait(500)

        self.assertEqual(len(spy), 1)
        self.assertEqual(self.task.state, state.FINISHED)
        self.assertEqual(self.task.status, status.COMPLETED)

        self.assertEqual(
            self.task.status_bar.currentMessage(),
            Logger.SSLKEYLOG_COMPLETED,
        )
        self.assertEqual(
            self.task.progress_bar.value(),
            (self.intial_progress_bar_value + self.increment),
        )

        self.assertTrue(os.path.exists(os.path.join(self.folder, "sslkey.log")))


if __name__ == "__main__":
    folder = resolve_path("tests/tasks/sslkeylog_test_folder")

    if not os.path.exists(folder):
        os.makedirs(folder)

    MainWindow = QtWidgets.QMainWindow()

    TaskSSLKeyLogTest.folder = folder
    TaskSSLKeyLogTest.acquisition = Acquisition(logger, folder)
    TaskSSLKeyLogTest.tasks_info = TasksInfo()
    TaskSSLKeyLogTest.window = Ui_MainWindow()
    TaskSSLKeyLogTest.window.setupUi(MainWindow)
    TaskSSLKeyLogTest.increment = TaskSSLKeyLogTest.acquisition.calculate_increment(1)

    TaskSSLKeyLogTest.acquisition.start()

    unittest.main()
