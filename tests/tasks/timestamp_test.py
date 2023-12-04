import os
import sys
import unittest

import logging

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QSignalSpy
from common.constants.view.tasks import labels, state, status


from view.acquisition.acquisition import Acquisition
from view.tasks.timestamp import TaskTimestamp

from common.utility import resolve_path
from common.constants import logger as Logger

from tests.tasks.tasks_ui import Ui_MainWindow

app = QApplication(sys.argv)

logger = logging.getLogger("view.web.web")


class TaskTimestampTest(unittest.TestCase):
    folder = ""
    acquisition = None
    pdf_filename = None
    window = None
    increment = 0
    dependencies = list()

    @classmethod
    def setUpClass(cls):
        options = {
            "acquisition_directory": cls.folder,
            "pdf_filename": cls.pdf_filename,
        }
        cls.task = TaskTimestamp(
            options,
            cls.acquisition.logger,
            cls.window.progressBar,
            cls.window.statusbar,
        )

        cls.intial_progress_bar_value = cls.window.progressBar.value()
        cls.task.increment = cls.increment
        cls.task.dependencies = cls.dependencies

    def test_00_init_headers_task(self):
        self.assertEqual(self.task.label, labels.TIMESTAMP)
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

        self.assertEqual(
            self.task.status_bar.currentMessage(),
            Logger.TIMESTAMP_STARTED,
        )

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
            Logger.TIMESTAMP_COMPLETED,
        )
        self.assertEqual(
            self.task.progress_bar.value(),
            (self.intial_progress_bar_value + self.increment),
        )

        self.assertTrue(os.path.exists(os.path.join(self.folder, "timestamp.tsr")))
        self.assertTrue(os.path.exists(os.path.join(self.folder, "tsa.crt")))


if __name__ == "__main__":
    folder = resolve_path("tests/tasks/timestamp_test_folder")

    if not os.path.exists(folder):
        os.makedirs(folder)

    MainWindow = QtWidgets.QMainWindow()

    TaskTimestampTest.folder = folder
    TaskTimestampTest.acquisition = Acquisition(logger, folder)
    TaskTimestampTest.window = Ui_MainWindow()
    TaskTimestampTest.window.setupUi(MainWindow)
    TaskTimestampTest.increment = TaskTimestampTest.acquisition.calculate_increment(1)

    TaskTimestampTest.pdf_filename = "acquisition_report.pdf"
    file = open(os.path.join(folder, TaskTimestampTest.pdf_filename), "w")
    file.write("This is not pdf file \n")
    file.close()

    TaskTimestampTest.acquisition.start()

    unittest.main()
