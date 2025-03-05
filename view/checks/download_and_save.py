from PyQt6 import QtCore, QtWidgets, QtWebEngineWidgets
from view.dialog import Dialog, DialogButtonTypes


class DownloadAndSave(QtWidgets.QDialog):
    finished = QtCore.pyqtSignal(str)

    def __init__(
        self, url, progress_dialog_title, progress_dialog_message, parent=None
    ):
        super(DownloadAndSave, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.file_path = None

        self.filename = QtCore.QUrl(url).path()
        self.suffix = QtCore.QFileInfo(self.filename).suffix()

        self.progress_dialog = Dialog(
            progress_dialog_title,
            progress_dialog_message,
        )
        self.progress_dialog.message.setStyleSheet("font-size: 13px;")
        self.progress_dialog.set_buttons_type(DialogButtonTypes.NONE)
        self.progress_dialog.show_progress_bar()
        self.progress_dialog.progress_bar.setValue(0)

        self.web_view = QtWebEngineWidgets.QWebEngineView()
        self.web_view.page().profile().downloadRequested.connect(
            self.on_download_requested
        )

        self.web_view.load(QtCore.QUrl(url))
        self.web_view.hide()

    def on_download_requested(self, download):
        self.file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save File", self.filename, "*." + self.suffix
        )

        if self.file_path:
            download.setDownloadFileName(self.file_path)
            download.accept()
            download.isFinishedChanged.connect(self.__is_download_finished)
            download.receivedBytesChanged.connect(
                lambda: self.__progress(
                    download.receivedBytes(),
                    download.totalBytes(),
                )
            )
            download.totalBytesChanged.connect(
                lambda: self.__progress(
                    download.receivedBytes(),
                    download.totalBytes(),
                )
            )
            self.progress_dialog.show()
        else:
            self.reject()

    def __is_download_finished(self):
        self.progress_dialog.close()
        self.finished.emit(self.file_path)

    def __progress(self, bytes_received, bytes_total):
        if bytes_total > 0:
            download_percentage = int(bytes_received * 100 / bytes_total)
            self.progress_dialog.progress_bar.setValue(download_percentage)
