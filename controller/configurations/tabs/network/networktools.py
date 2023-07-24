from model.configurations.tabs.network.networktools import NetworkTools as NetworkToolsModel

class NetworkTools():

    _configuration = {}

    def __init__(self):
        self.model = NetworkToolsModel()
        self._configuration = self.model.get()
        if self._configuration:
           self._configuration = {key: value for key, value in self._configuration[0].__dict__.items() if not key.startswith("_") and not key.startswith("__") and not key.startswith("db")}

    @property
    def configuration(self):
        return self._configuration

    @configuration.setter
    def configuration(self, configuration):
        self.model.update(configuration)

