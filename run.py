# -*- coding: utf-8 -*-
import gevent, gevent.server, gevent.monkey
import config, tools, signal, sys
from sockets.server import Sockets

reload(sys)
sys.setdefaultencoding("utf-8")

if __name__ == '__main__':
  gevent.monkey.patch_all()
  server = (config.Server.ip, config.Server.port)

  tools.log.info('[Server] Starting FyIRCd, listening on %s:%s' % server)
  server = gevent.server.StreamServer(server, Sockets.handle, spawn=10000)

  gevent.signal(signal.SIGTERM, server.stop)
  gevent.signal(signal.SIGINT, server.stop)
  server.serve_forever()
  tools.log.info('Server stopped')
