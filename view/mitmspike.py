from mitmproxy import http
from mitmproxy import flow
from mitmproxy import ctx

class AddHeader:
    def response(self, flow: http.HTTPFlow):
        flow.response.headers["new-header"] = "new-value"

addons = [
    AddHeader()
]

def start():
    ctx.log("mitmproxy started")

def request(flow: http.HTTPFlow):
    flow.request.headers["my-header"] = "my-value"

def response(flow: http.HTTPFlow):
    print(flow.response.headers)

if __name__ == '__main__':
    from mitmproxy.tools.main import mitmdump

    mitmdump(['-s', 'C:\\Users\\Routi\\fit\\view\\test.py'])