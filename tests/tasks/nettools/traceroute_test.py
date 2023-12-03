import os
import sys
import unittest

import logging

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QSignalSpy
from common.constants.view.tasks import labels, state, status


from view.acquisition.acquisition import Acquisition
from view.tasks.tasks_info import TasksInfo
from view.tasks.nettools.traceroute import TaskTraceroute

from common.utility import resolve_path
from common.constants import logger as Logger

from tests.tasks.tasks_ui import Ui_MainWindow

app = QApplication(sys.argv)


class TaskTracerouteTest(unittest.TestCase):
    folder = ""
    window = None
    increment = 100

    @classmethod
    def setUpClass(cls):
        cls.task = TaskTraceroute(
            logging.getLogger("view.scrapers.web.web"),
            cls.window.progressBar,
            cls.window.statusbar,
        )

        cls.task.options = {
            "acquisition_directory": cls.folder,
            "url": "https://google.it",
        }
        cls.intial_progress_bar_value = cls.window.progressBar.value()
        cls.task.increment = cls.increment

    def test_00_init_headers_task(self):
        self.assertEqual(self.task.label, labels.TRACEROUTE)
        self.assertEqual(self.task.state, state.INITIALIZATED)
        self.assertEqual(self.task.status, status.SUCCESS)

    def test_01_headers_task(self):
        spy = QSignalSpy(self.task.started)

        self.task.start()

        if len(spy) == 0:
            received = spy.wait(500)
            while received is False:
                received = spy.wait(500)

        self.assertEqual(len(spy), 1)

        self.assertEqual(self.task.state, state.STARTED)
        self.assertEqual(self.task.status, status.SUCCESS)

        self.assertEqual(
            self.task.status_bar.currentMessage(),
            Logger.TRACEROUTE_STARTED,
        )
        self.assertEqual(self.task.progress_bar.value(), 0)

        spy = QSignalSpy(self.task.finished)

        if len(spy) == 0:
            received = spy.wait(500)
            while received is False:
                received = spy.wait(500)

        self.assertEqual(len(spy), 1)
        self.assertEqual(self.task.state, state.COMPLETED)
        self.assertEqual(self.task.status, status.SUCCESS)

        self.assertEqual(
            self.task.status_bar.currentMessage(),
            Logger.TRACEROUTE_COMPLETED,
        )
        self.assertEqual(
            self.task.progress_bar.value(),
            (self.intial_progress_bar_value + self.increment),
        )

        self.assertTrue(os.path.exists(os.path.join(self.folder, "traceroute.txt")))


if __name__ == "__main__":
    folder = resolve_path("tests/tasks/traceroute_test_folder")

    if not os.path.exists(folder):
        os.makedirs(folder)

    MainWindow = QtWidgets.QMainWindow()

    TaskTracerouteTest.folder = folder
    TaskTracerouteTest.window = Ui_MainWindow()
    TaskTracerouteTest.window.setupUi(MainWindow)

    unittest.main()
