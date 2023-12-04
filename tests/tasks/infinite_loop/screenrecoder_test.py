import os
import time
import sys
import unittest
import logging

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QSignalSpy
from common.constants.view.tasks import labels, state, status


from view.acquisition.acquisition import Acquisition
from view.tasks.info import TasksInfo
from view.tasks.infinite_loop.screenrecorder import TaskScreenRecorder


from common.utility import resolve_path
from common.constants import details, logger as Logger

from tests.tasks.tasks_ui import Ui_MainWindow

app = QApplication(sys.argv)

logger = logging.getLogger("view.web.web")


class TaskScreenRecorderTest(unittest.TestCase):
    folder = ""
    acquisition = None
    tasks_info = None
    window = None
    increment = 0

    @classmethod
    def setUpClass(cls):
        options = {"acquisition_directory": cls.folder}

        cls.task = TaskScreenRecorder(
            options,
            cls.acquisition.logger,
            cls.tasks_info,
            cls.window.progressBar,
            cls.window.statusbar,
        )

        cls.intial_progress_bar_value = cls.window.progressBar.value()
        cls.task.increment = cls.increment

    def test_00_init_screen_recorder_task(self):
        self.assertEqual(self.task.label, labels.SCREEN_RECORDER)
        self.assertEqual(self.task.state, state.INITIALIZATED)
        self.assertEqual(self.task.status, status.DONE)
        self.assertEqual(self.task.progress_bar.value(), 0)

        row = self.tasks_info.get_row(labels.SCREEN_RECORDER)
        if row >= 0:
            self.assertEqual(
                self.task.state,
                self.tasks_info.table.item(row, 1).text(),
            )
            self.assertEqual(
                self.task.status,
                self.tasks_info.table.item(row, 2).text(),
            )

    def test_01_screen_recorder_task(self):
        spy = QSignalSpy(self.task.started)
        self.task.start()
        self.assertEqual(self.task.state, state.STARTED)
        self.assertEqual(self.task.status, status.PENDING)
        self.assertEqual(
            self.task.status_bar.currentMessage(),
            Logger.SCREEN_RECODER_STARTED,
        )
        self.assertEqual(self.task.progress_bar.value(), 0)
        if len(spy) == 0:
            received = spy.wait(500)
            while received is False:
                received = spy.wait(500)

        self.assertEqual(len(spy), 1)

        self.assertEqual(self.task.state, state.STARTED)
        self.assertEqual(self.task.status, status.SUCCESS)
        self.assertEqual(self.task.details, details.SCREEN_RECORDER_STARTED)

        time.sleep(5)

        spy = QSignalSpy(self.task.finished)
        self.task.stop()

        if len(spy) == 0:
            received = spy.wait(500)
            while received is False:
                received = spy.wait(500)

        self.assertEqual(len(spy), 1)
        self.assertEqual(self.task.state, state.COMPLETED)
        self.assertEqual(self.task.status, status.SUCCESS)
        self.assertEqual(self.task.details, details.SCREEN_RECORDER_COMPLETED)
        self.assertEqual(
            self.task.status_bar.currentMessage(),
            Logger.SCREEN_RECODER_COMPLETED,
        )
        self.assertEqual(
            self.task.progress_bar.value(),
            (self.intial_progress_bar_value + self.increment),
        )

        self.assertTrue(os.path.exists(self.task.options["filename"]))


if __name__ == "__main__":
    folder = resolve_path("tests/tasks/screenrecorder_test_folder")

    if not os.path.exists(folder):
        os.makedirs(folder)

    MainWindow = QtWidgets.QMainWindow()

    TaskScreenRecorderTest.folder = folder
    TaskScreenRecorderTest.acquisition = Acquisition(logger, folder)
    TaskScreenRecorderTest.tasks_info = TasksInfo()
    TaskScreenRecorderTest.window = Ui_MainWindow()
    TaskScreenRecorderTest.window.setupUi(MainWindow)
    TaskScreenRecorderTest.increment = (
        TaskScreenRecorderTest.acquisition.calculate_increment(1)
    )

    TaskScreenRecorderTest.acquisition.start()

    unittest.main()
