import os
import sys
import unittest

import logging

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QSignalSpy
from common.constants.view.tasks import labels, state, status


from view.acquisition.acquisition import Acquisition
from view.tasks.info import TasksInfo
from view.tasks.pec.pec_and_download_eml import TaskPecAndDownloadEml

from common.utility import resolve_path
from common.constants import logger as Logger

from tests.tasks.tasks_ui import Ui_MainWindow

app = QApplication(sys.argv)

logger = logging.getLogger("view.web.web")


class TaskPecAndDownloadEmlTest(unittest.TestCase):
    folder = ""
    acquisition = None
    tasks_info = None
    window = None
    increment = 0

    @classmethod
    def setUpClass(cls):
        cls.pdf_filename = "acquisition_report.pdf"

        file = open(os.path.join(cls.folder, cls.pdf_filename), "w")
        file.write("This is not pdf file \n")
        file.close()

        cls.tsr_filename = "timestamp.tsr"

        file = open(os.path.join(cls.folder, cls.tsr_filename), "w")
        file.write("This is not tsr file \n")
        file.close()

        cls.crt_filename = "tsa.crt"

        file = open(os.path.join(cls.folder, cls.crt_filename), "w")
        file.write("This is not crt file \n")
        file.close()

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
        cls.task = TaskPecAndDownloadEml(
            options,
            cls.acquisition.logger,
            cls.tasks_info,
            cls.window.progressBar,
            cls.window.statusbar,
        )

        cls.intial_progress_bar_value = cls.window.progressBar.value()
        cls.task.increment = cls.increment

    def test_00_init_headers_task(self):
        self.assertEqual(self.task.label, labels.PEC_AND_DOWNLOAD_EML)
        self.assertEqual(self.task.state, state.INITIALIZATED)
        self.assertEqual(self.task.status, status.DONE)
        self.assertEqual(self.task.progress_bar.value(), 0)

        row = self.tasks_info.get_row(labels.PEC_AND_DOWNLOAD_EML)
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
            Logger.PEC_AND_DOWNLOAD_EML_STARTED,
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
            Logger.PEC_AND_DOWNLOAD_EML_COMPLETED,
        )
        self.assertEqual(
            self.task.progress_bar.value(),
            (self.intial_progress_bar_value + self.increment * 2),
        )

        # self.assertTrue(
        #     os.path.exists(os.path.join(self.folder, "acquisition_report.pdf"))
        # )


if __name__ == "__main__":
    folder = resolve_path("tests/tasks/pec_and_download_eml_test_folder")

    if not os.path.exists(folder):
        os.makedirs(folder)

    MainWindow = QtWidgets.QMainWindow()

    TaskPecAndDownloadEmlTest.folder = folder
    TaskPecAndDownloadEmlTest.acquisition = Acquisition(logger, folder)
    TaskPecAndDownloadEmlTest.tasks_info = TasksInfo()
    TaskPecAndDownloadEmlTest.window = Ui_MainWindow()
    TaskPecAndDownloadEmlTest.window.setupUi(MainWindow)
    TaskPecAndDownloadEmlTest.increment = (
        TaskPecAndDownloadEmlTest.acquisition.calculate_increment(2)
    )

    TaskPecAndDownloadEmlTest.acquisition.start()

    unittest.main()
