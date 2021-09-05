import threading
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server
from prometheus_client import CollectorRegistry
from prometheus_client.core import REGISTRY
from prometheus_client.exposition import choose_encoder, ThreadingWSGIServer, _SilentHandler, _bake_output

from .collector import GenesysSIPServerCollector

def make_wsgi_app(registry=REGISTRY):
  """Create a WSGI app which serves the metrics from a registry."""

  def prometheus_app(environ, start_response):
      # Prepare parameters
      accept_header = environ.get('HTTP_ACCEPT')
      params = parse_qs(environ.get('QUERY_STRING', ''))

      target = 'target' in params and params.get('target') or None
      if target is None:
        registry.set_target_info(None)
      else:
        registry.set_target_info({"target": target[0]})

      if environ['PATH_INFO'] == '/favicon.ico':
          # Serve empty response for browsers
          status = '200 OK'
          header = ('', '')
          output = b''
      else:
          # Bake output
          status, header, output = _bake_output(registry, accept_header, params)
      # Return output
      start_response(status, [header])
      return [output]

  return prometheus_app

def start_wsgi_server(port, addr='', registry=REGISTRY):
    """Starts a WSGI server for prometheus metrics as a daemon thread."""
    app = make_wsgi_app(registry)
    httpd = make_server(addr, port, app, ThreadingWSGIServer, handler_class=_SilentHandler)
    t = threading.Thread(target=httpd.serve_forever)
    # t.daemon = True
    t.start()

def main():
  registry = CollectorRegistry(auto_describe=True)
  GenesysSIPServerCollector(registry=registry)

  start_wsgi_server(8001, registry=registry)

if __name__ == '__main__':
  main()
