import aceclient, threading, BaseHTTPServer, SocketServer, urllib2

class AceSettings:
  acehost = '127.0.0.1'
  aceport = 62062
  acetimeout = 5
  acedebug = True

class AceHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  def do_GET(self):
    try:
      #Creating new AceClient
      self._aceclient = aceclient.AceClient(AceSettings.acehost, AceSettings.aceport, AceSettings.acetimeout, 
					    AceSettings.acedebug)
      self._url = self._aceclient.getUrl(self.path.split('/')[1])
      self._stream = urllib2.urlopen(self._url)
      
      if self._url and self._stream:
	self.send_response(200)
	self.end_headers()
	while True:
	  try:
	    self.wfile.write(self._stream.read(8192))
	  except:
	    # Closed connection
	    print "DESTROYING ACE!!!!"
	    self._aceclient.destroy()
      else:
	self.send_error(500)
	self.end_headers()
    except Exception as e:
      self.send_error(500)
      self.end_headers()
      try:
	self._aceclient.destroy()
      except:
	pass
      
      
class AceServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
  pass
      
server = AceServer(("0.0.0.0", 8000), AceHandler)
try:
  server.serve_forever()
except KeyboardInterrupt:
  print "interrupt"
  pass
server.server_close()
