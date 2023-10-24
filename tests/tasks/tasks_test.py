import os

import unittest
import logging

from view.acquisition.acquisition import Acquisition
from view.tasks.info import TasksInfo

from common.utility import resolve_path
from tests.tasks.screenrecoder_test import TaskScreenRecorderTest
from tests.tasks.packetcapture_test import TaskPacketCaptureTest


logger = logging.getLogger("view.web.web")


if __name__ == "__main__":
    folder = resolve_path("tests/tasks/tasks_test_folder")

    if not os.path.exists(folder):
        os.makedirs(folder)

    acquisition = Acquisition(logger, folder)
    tasks_info = TasksInfo()

    TaskScreenRecorderTest.folder = folder
    TaskScreenRecorderTest.acquisition = acquisition
    TaskScreenRecorderTest.tasks_info = tasks_info

    TaskPacketCaptureTest.folder = folder
    TaskPacketCaptureTest.acquisition = acquisition
    TaskPacketCaptureTest.tasks_info = tasks_info

    acquisition.start()

    # Load each tasks
    tc1 = unittest.TestLoader().loadTestsFromTestCase(TaskScreenRecorderTest)
    tc2 = unittest.TestLoader().loadTestsFromTestCase(TaskPacketCaptureTest)

    # Create a test suite combining all test classes
    Test1 = unittest.TestSuite([tc1, tc2])
    unittest.TextTestRunner(verbosity=2).run(Test1)

    # Create a test suite to run single test class
    # Test1 = unittest.TestSuite([tc1])
    # Test2 = unittest.TestSuite([tc2])
    # unittest.TextTestRunner(verbosity=2).run(Test1)
    # unittest.TextTestRunner(verbosity=2).run(Test2)

    acquisition.stop()
