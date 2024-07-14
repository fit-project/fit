import sys
import logging

from PyQt6.QtGui import QGuiApplication
from PyQt6 import QtWidgets, uic
from common.utility import resolve_path

from view.tasks.infinite_loop.screenrecorder import TaskScreenRecorder

logger = logging.getLogger("view.web.web")

import ffmpeg_downloader as ffdl
import subprocess
import json
import re


def audio_video_device_list():
    proc = subprocess.Popen(
        [
            ffdl.ffmpeg_path,
            "-stats",
            "-hide_banner",
            "-list_devices",
            "true",
            "-f",
            "dshow",
            "-i",
            "dummy",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    stdout, stderr = proc.communicate()
    json_object = json.dumps(stderr.decode("UTF-8"))
    json_object = json.loads(json_object)

    for x in json_object.split("\n"):
        if x.__contains__("audio"):
            print(re.findall(r'"([^"]*)"', x)[0].__contains__("@device"))
            print(re.findall(r'"([^"]*)"', x)[0])
            print(re.findall(r'"([^"]*)"', x)[0])
        if x.__contains__("video"):
            print(re.findall(r'"([^"]*)"', x)[0].__contains__("@device"))
            print(re.findall(r'"([^"]*)"', x)[0])
            print(re.findall(r'"([^"]*)"', x)[0])


# def process(obj,args):
#         for x in json_object.split("\n"):
#             try:
#                 if x.__contains__(f"{obj.device_type}"):
#                     if re.findall(r'"([^"]*)"', x )[0].__contains__("@device") == False:
#                         only_video_json_object.append("DEVICE NAME : " + re.findall(r'"([^"]*)"', x )[0] )
#                         cont = True
#                 if cont == True:
#                     if (obj.alt_name == True or args.alternative == True) and re.findall(r'"([^"]*)"', x )[0].__contains__("@device") == True:
#                         only_video_json_object.append("ALTERNATIVE NAME : " +  re.findall(r'"([^"]*)"', x )[0] + "\n")
#                         cont = False
#             except:
#                 continue
#         if obj.list_all == True:
#             print_all()
#         if obj.save == True:
#             save()


class StartAdnStopTask(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(StartAdnStopTask, self).__init__(parent)
        uic.loadUi(resolve_path("tests/ui/tasks/start_and_stop_task.ui"), self)

        self.task = TaskScreenRecorder(
            logger,
            self.progress_bar,
            self.status_message,
            self,
        )
        self.task.options = {"acquisition_directory": ""}
        self.task.increment = 0

        self.start.clicked.connect(self.task.start)
        self.stop.clicked.connect(self.task.stop)

        self.task.started.connect(self.__print_message)
        self.task.finished.connect(self.__print_message)

        for screen in QGuiApplication.screens():
            print(screen.name())
            print(screen.manufacturer())

        # audio_video_device_list()

    def __print_message(self):
        self.message.setText(
            "State: {} <br> Status: {} <br> Details: {}".format(
                self.task.state, self.task.status, self.task.details
            )
        )


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = StartAdnStopTask()
    w.show()
    sys.exit(app.exec())
