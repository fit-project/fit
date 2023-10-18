import os
import time
import sys
import unittest
import logging


from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QSignalSpy


from view.acquisition.acquisition import Acquisition
from view.tasks.info import TasksInfo
from view.tasks.screenrecorder import TaskScreenRecorder

from common.constants import logger, details, state, status, tasks

app = QApplication(sys.argv)

logger = logging.getLogger("view.web")


class AcquisitionTest(unittest.TestCase):
    def setUp(self):
        folder = "acquisition_folder_test"

        if not os.path.exists(folder):
            os.makedirs(folder)

        self.acquisition = Acquisition(logger, folder)
        self.tasks_info = TasksInfo()

        options = {"acquisition_directory": folder}

        self.screen_recorder_task = TaskScreenRecorder(
            options, self.acquisition.logger, self.tasks_info
        )

        self.acquisition.start()

    def test_resolve_path(self):
        path = __file__
        if getattr(sys, "frozen", False):
            # If the 'frozen' flag is set, we are in bundled-app mode!
            resolved_path = os.path.abspath(os.path.join(sys._MEIPASS, path))
        else:
            # Normal development mode. Use os.getcwd() or __file__ as appropriate in your case...
            resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))

        print(resolved_path)

    # def test_init(self):
    #     self.assertEqual(self.screen_recorder_task.name, tasks.SCREEN_RECORDER)
    #     self.assertEqual(self.screen_recorder_task.state, state.INITIALIZATED)
    #     self.assertEqual(self.screen_recorder_task.status, status.DONE)

    #     row = self.tasks_info.get_row(tasks.SCREEN_RECORDER)
    #     if row >= 0:
    #         self.assertEqual(
    #             self.screen_recorder_task.state,
    #             self.tasks_info.table.item(row, 1).text(),
    #         )
    #         self.assertEqual(
    #             self.screen_recorder_task.status,
    #             self.tasks_info.table.item(row, 2).text(),
    #         )

    # def test_screen_recorder_task(self):
    #     spy = QSignalSpy(self.screen_recorder_task.started)
    #     self.screen_recorder_task.start()
    #     self.assertEqual(self.screen_recorder_task.state, state.STARTED)
    #     self.assertEqual(self.screen_recorder_task.status, status.PENDING)

    #     received = spy.wait(500)
    #     while received is False:
    #         received = spy.wait(500)

    #     self.assertEqual(len(spy), 1)

    #     self.assertEqual(self.screen_recorder_task.state, state.STARTED)
    #     self.assertEqual(self.screen_recorder_task.status, status.COMPLETED)
    #     self.assertEqual(
    #         self.screen_recorder_task.details, details.SCREEN_RECORDER_STARTED
    #     )

    #     time.sleep(5)

    #     spy = QSignalSpy(self.screen_recorder_task.finished)
    #     self.screen_recorder_task.stop()

    #     self.assertEqual(self.screen_recorder_task.state, state.STOPPED)
    #     self.assertEqual(self.screen_recorder_task.status, status.PENDING)

    #     received = spy.wait(500)
    #     while received is False:
    #         received = spy.wait(500)

    #     self.assertEqual(len(spy), 1)
    #     self.assertEqual(self.screen_recorder_task.state, state.FINISHED)
    #     self.assertEqual(self.screen_recorder_task.status, status.COMPLETED)
    #     self.assertEqual(
    #         self.screen_recorder_task.details, details.SCREEN_RECORDER_COMPLETED
    #     )

    # def delete_folder(self):
    #     pass


if __name__ == "__main__":
    unittest.main()
