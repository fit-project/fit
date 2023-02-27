import hashlib
import os
import re
import ssl
import sys
import asyncio
from datetime import datetime
from io import BytesIO
from types import SimpleNamespace

import certifi
import mitmproxy.http
from PyQt5.QtCore import QUrl, QObject, pyqtSignal, QThread
import logging

from PyQt5.QtNetwork import QNetworkProxy, QSslCertificate, QSslConfiguration
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtWidgets import QApplication
from mitmproxy import utils, http
from mitmproxy.tools import main
from mitmproxy.tools.dump import DumpMaster
from warcio import StatusAndHeaders
from warcio.warcwriter import WARCWriter
from wacz.main import create_wacz


class ProxyServer(QObject):
    # logging.basicConfig(filename='mitmproxy.log', level=logging.INFO)
    proxy_started = pyqtSignal(int)

    def __init__(self, port):
        super().__init__()
        self.port = port

    async def start(self):
        # set proxy opts
        options = main.options.Options(listen_host='127.0.0.1', listen_port=self.port,
                                       ssl_insecure=True)
        master = DumpMaster(options=options)

        # addons in mitmproxy are used to provide additional features and customize proxy's behavior
        # this way, we can create custom addons to intercept everything and create the warc/wacz files

        master.addons.add(FlowReaderAddon())

        try:
            await master.run()
        except KeyboardInterrupt:
            master.shutdown()


# creating a custom addon to save flow as warc
def FlowToWarc(flow: http.HTTPFlow):
    warc_file = 'resources/test_warc.warc'
    with open(warc_file, 'ab') as output:
        # create new warcio writer
        writer = WARCWriter(output, gzip=False)
        if len(flow.response.content) > 0:
            content_type = flow.response.headers.get('content-type', '').split(';')[0]
            payload = flow.response.content

            headers = flow.response.headers.items()

            # date from flow is returning as float, needs to be converted
            date_obj = datetime.fromtimestamp(flow.response.timestamp_start)
            # convert the datetime object to an ISO formatted string
            iso_date_str = date_obj.isoformat()

            # create http headers from the information inside the flow
            http_headers = StatusAndHeaders(str(flow.response.status_code) + ' ' + flow.response.reason, headers,
                                            protocol=flow.response.http_version)
            warc_headers = {
                'WARC-Type': 'resource',
                'WARC-Target-URI': flow.request.url,
                'WARC-Source-URI': flow.request.url,
                'WARC-Date': iso_date_str,
                'Content-Type': content_type,
                'Content-Length': str(len(payload))
            }
            # check if payload is in bytes format
            if type(payload) is bytes:
                payload = BytesIO(payload)

            # create the actual warc record
            record = writer.create_warc_record(flow.request.url, 'resource',
                                               payload=payload,
                                               http_headers=http_headers,
                                               warc_headers_dict=warc_headers)
            writer.write_record(record)


def WarcToWacz(warc_path):
    class OptionalNamespace(SimpleNamespace):
        def __getattribute__(self, name):
            try:
                return super().__getattribute__(name)
            except:
                return None

    res = OptionalNamespace(
        output='resources/test_wacz.wacz',
        inputs=[warc_path],
        detect_pages=True
    )
    return create_wacz(res)


# creating a custom addon to intercept requests and reponses, printing url, status code, headers and content
class FlowReaderAddon:
    def __init__(self):
        self.resources = []

    def request(self, flow: mitmproxy.http.HTTPFlow):
        # print just for fun

        # print("Request URL: " + flow.request.url)
        # print("Request Headers: " + str(flow.request.headers))
        # print("Request Content: " + str(flow.request.content))
        pass

    def response(self, flow: mitmproxy.http.HTTPFlow):
        #TODO: search a better way to get the resource's name (for same-host resources)
        if len(flow.response.content) > 0:
            url = flow.request.url
            # save html first (since it has no extension in the flow)
            if flow.response.headers.get('content-type', '').startswith('text/html'):
                # get html to disk
                html_text = flow.response.content
                with open(f"resources/{flow.request.pretty_host}.html", "wb") as f:
                    f.write(html_text)

            # get extension for other resources
            content_type = flow.response.headers.get('content-type', '').lower()
            extension = re.search(r'\b(?!text\/)(\w+)\/(\w+)', content_type)
            if extension:
                extension = '.' + extension.group(2)
            else:
                extension = None

            if extension is not None:

                if flow.response.headers.get('content-type', '').split(';')[0].startswith('image/'):
                    # save image to disk
                    with open(f"resources/{hashlib.md5(url.encode()).hexdigest()}{extension}", "wb") as f:
                        f.write(flow.response.content)
                    self.resources.append(flow.request.url)
                else:
                    # save other resources to disk
                    with open(f"resources/{hashlib.md5(url.encode()).hexdigest()}{extension}", "wb") as f:
                        f.write(flow.response.content)
                    self.resources.append(flow.request.url)
            # create the warc file from the flow
        FlowToWarc(flow)


# the proxy needs to be started on a different thread
class MitmThread(QThread):
    def __init__(self, port):
        super().__init__()
        self.port = port

    def run(self):
        # create new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # mitmproxy's creation
        proxy_server = ProxyServer(self.port)
        asyncio.get_event_loop().run_until_complete(proxy_server.start())


# create the qwebengineview, set the proxy certificate and start the thread
class MainWindow(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)

        der_data = set_ssl_config()
        pem_data = ssl.DER_cert_to_PEM_cert(der_data)
        self.page().profile().clearHttpCache()
        self.page().profile().setHttpUserAgent(pem_data)

        # set port and start the thread (while creating the mainwindow)
        port = 8081
        self.mitm_thread = MitmThread(port)
        self.mitm_thread.start()

        url = QUrl("https://www.google.com/")
        super().load(url)

    def closeEvent(self, event):
        #create wacz when window is closed
        warc_file = 'resources/test_warc.warc'
        WarcToWacz(warc_file)


# ssl configurations (not working for me, I had to install the certificate on my machine)
def set_ssl_config():
    # get the pem with openssl from the mitmproxy .p12
    # openssl pkcs12 -in {mitmproxy-ca-cert.p12} -out {cert_pem} -nodes

    # add pem to the trusted root certificates (won't solve the problem)
    cert_file_path = certifi.where()
    pem_path = 'C:\\Users\\Routi\\Downloads\\mitmproxy-ca-cert.pem'
    with open(pem_path, 'rb') as pem_file:
        pem_data = pem_file.read()
    with open(cert_file_path, 'ab') as cert_file:
        cert_file.write(pem_data)

    # create a QSslConfiguration object with the certificate as the CA certificate (won't solve the problem neither)
    cert = QSslCertificate(pem_data)
    config = QSslConfiguration.defaultConfiguration()
    config.setCaCertificates([cert])

    # get the DER-encoded certificate data
    der_data = cert.toDer()
    return der_data


if __name__ == "__main__":
    app = QApplication(sys.argv)

    if not os.path.isdir("resources"):
        os.makedirs("resources")

    webview = MainWindow()
    # create the proxy
    proxy = QNetworkProxy(QNetworkProxy.HttpProxy, '127.0.0.1', 8081)
    QNetworkProxy.setApplicationProxy(proxy)


    webview.show()

    sys.exit(app.exec_())

