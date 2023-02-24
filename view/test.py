import requests
from PyQt5 import QtCore, QtGui, QtWidgets, QtNetwork

class Ui_MainWindow(object):
    ...

from PyQt5 import QtWebEngineWidgets

if __name__ == "__main__":
   import sys
   app = QtWidgets.QApplication(sys.argv)

   proxy = QtNetwork.QNetworkProxy()
   proxy.setType(QtNetwork.QNetworkProxy.HttpProxy)
   proxy.setHostName("127.0.0.1")
   proxy.setPort(8080)
   QtNetwork.QNetworkProxy.setApplicationProxy(proxy)
   proxy.applicationProxy()
   MainWindow = QtWidgets.QMainWindow()
   ui = Ui_MainWindow()
   ui.setupUi(MainWindow)
   MainWindow.show()
   sys.exit(app.exec_())

   cert_file = QFile("mycert.pem")
   cert_file.open(QIODevice.ReadOnly)
   cert = QSslCertificate(cert_file)
   cert_file.close()
   manager = QNetworkAccessManager()
   manager.addCaCertificate(cert)
   import requests
   requests.get('https://www.google.com')