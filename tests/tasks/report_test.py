import os
import sys
import unittest

import logging

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QSignalSpy
from common.constants.view.tasks import labels, state, status


from view.acquisition.acquisition import Acquisition
from view.tasks.report import TaskReport

from common.utility import resolve_path
from common.constants import logger as Logger

from tests.tasks.tasks_ui import Ui_MainWindow

app = QApplication(sys.argv)

logger = logging.getLogger("view.web.web")


class TaskReportTest(unittest.TestCase):
    folder = ""
    acquisition = None
    tasks_info = None
    window = None
    increment = 0

    @classmethod
    def setUpClass(cls):
        case_info = {
            "id": 1,
            "name": "Go out",
            "lawyer_name": "",
            "operator": "",
            "proceeding_type": 1,
            "courthouse": "",
            "proceeding_number": "",
            "notes": "",
            "logo_bin": "",
            "logo": "",
            "logo_height": "",
            "logo_width": "",
        }
        options = {
            "acquisition_directory": cls.folder,
            "type": "web",
            "case_info": case_info,
        }
        cls.task = TaskReport(
            options,
            cls.acquisition.logger,
            cls.window.progressBar,
            cls.window.statusbar,
        )

        cls.intial_progress_bar_value = cls.window.progressBar.value()
        cls.task.increment = cls.increment

    def test_00_init_headers_task(self):
        self.assertEqual(self.task.label, labels.REPORTFILE)
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
            Logger.GENERATE_PDF_REPORT_STARTED,
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
            Logger.GENERATE_PDF_REPORT_COMPLETED,
        )
        self.assertEqual(
            self.task.progress_bar.value(),
            (self.intial_progress_bar_value + self.increment),
        )

        self.assertTrue(
            os.path.exists(os.path.join(self.folder, "acquisition_report.pdf"))
        )


if __name__ == "__main__":
    folder = resolve_path("tests/tasks/report_test_folder")

    if not os.path.exists(folder):
        os.makedirs(folder)

    MainWindow = QtWidgets.QMainWindow()

    TaskReportTest.folder = folder
    TaskReportTest.acquisition = Acquisition(logger, folder)
    TaskReportTest.window = Ui_MainWindow()
    TaskReportTest.window.setupUi(MainWindow)
    TaskReportTest.increment = TaskReportTest.acquisition.calculate_increment(1)

    TaskReportTest.acquisition.start()

    unittest.main()
