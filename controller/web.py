import os.path

from PyQt5.QtCore import QEventLoop, QFile, QTextStream
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings


class Web:
    def __init__(self, url, acquisition_page):
        self.url = url
        self.acquisition_page = acquisition_page


    def save_html(self):
        web_view = QWebEngineView()
        self.page = web_view.page()
        self.page.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        self.page.loadFinished.connect(self.page_loaded)
        self.page.load(self.url)

        self.loop = QEventLoop()
        self.html_content = None
        self.loop.exec_()

        if self.html_content is not None:
            file = QFile(os.path.join(self.acquisition_page, 'index.html'))
            file.open(QFile.WriteOnly | QFile.Truncate)
            out = QTextStream(file)
            out.setCodec("UTF-8")
            out << self.html_content
            file.close()

    def handle_html(self, content: str):
        self.html_content = content
        self.page.save('test.html')
        self.loop.quit()

    def page_loaded(self, ok):
        if ok:
            self.page.toHtml(self.handle_html)
        else:
            self.loop.quit()


