import os

import unittest
import logging

from view.acquisition.acquisition import Acquisition
from view.tasks.info import TasksInfo

from common.utility import resolve_path
from tests.tasks.screenrecoder_test import ScreenRecorderTest
from tests.tasks.packetcapture_test import PacketCaptureTest


logger = logging.getLogger("view.web.web")


if __name__ == "__main__":
    folder = resolve_path("tests/tasks/tasks_test_folder")

    if not os.path.exists(folder):
        os.makedirs(folder)

    acquisition = Acquisition(logger, folder)
    tasks_info = TasksInfo()

    ScreenRecorderTest.folder = folder
    ScreenRecorderTest.acquisition = acquisition
    ScreenRecorderTest.tasks_info = tasks_info

    PacketCaptureTest.folder = folder
    PacketCaptureTest.acquisition = acquisition
    PacketCaptureTest.tasks_info = tasks_info

    acquisition.start()

    # Load each tasks
    tc1 = unittest.TestLoader().loadTestsFromTestCase(ScreenRecorderTest)
    tc2 = unittest.TestLoader().loadTestsFromTestCase(PacketCaptureTest)

    # Create a test suite combining all test classes
    Test1 = unittest.TestSuite([tc1, tc2])
    unittest.TextTestRunner(verbosity=2).run(Test1)

    # Create a test suite to run single test class
    # Test1 = unittest.TestSuite([tc1])
    # Test2 = unittest.TestSuite([tc2])
    # unittest.TextTestRunner(verbosity=2).run(Test1)
    # unittest.TextTestRunner(verbosity=2).run(Test2)

    acquisition.stop()
