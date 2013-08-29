# Based on telnetlib
import telnetlib
import threading

class AceException(Exception):
  pass

class AceCommands:
  ACE_HELLO = 'HELLOBG version=3'
  ACE_SHUTDOWN = 'SHUTDOWN'
  ACE_READY = 'READY'
  
  @staticmethod
  def ACE_USERDATA(gender, age):
    return 'USERDATA [{"gender": '+str(gender)+'}, {"age": '+str(age)+'}]' # Not important yet
  
  @staticmethod
  def ACE_START(cid):
    return 'START PID '+cid+' 0'

class AceClient:
  def __init__(self, host, port, timeout, debug = False):
    # Receive buffer
    self._recvbuffer = None
    # Stream URL
    self._url = None
    self._socket = None
    self._event = threading.Event()
    self._recvThread = None
    self._shuttingDown = False
    self._debug = debug
    self._status = None
    self._state = None
    
    try:
      self._socket = telnetlib.Telnet(host, port, timeout)
    except Exception as e:
      raise AceException("Socket creation error!" + e)
    
    self._recvThread = threading.Thread(name="AceClientThread", target=self._recvData)
    self._recvThread.start()
    self.__debug("Receive thread started!")
    
    self._aceInit()
    
  def __debug(self, message):
    if self._debug:
      print "AceClient: "+message
    
  def __del__(self):
    if self._socket:
      self.destroy()
    
  def destroy(self):
    self.__debug("Destroying...")
    self._shuttingDown = True
    self._write(AceCommands.ACE_SHUTDOWN)
    self._socket = None
    self._recvThread.join()
    
  def _write(self, message):
    self._socket.write(message + "\r\n")
    
  def _aceInit(self):
    self._write(AceCommands.ACE_HELLO)
    self._write(AceCommands.ACE_READY)
    self._write(AceCommands.ACE_USERDATA(1,3))
    
  def getUrl(self, cid):
    self._event.clear()
    self._write(AceCommands.ACE_START(cid))
    # Waiting for event from _recvData
    self._event.wait(60)
    self.__debug("Got URL: "+self._url)
    return self._url
    
  def _recvData(self):
    while True:
      if self._shuttingDown:
	break
      try:
	self._recvbuffer = self._socket.read_until("\r\n", 2)
      except EOFError as e:
	if self._shuttingDown:
	  pass
	else:
	  raise EOFError(e)
	
      if self._recvbuffer.startswith("STATUS"):
	# Parse STATUS
	self._status = self._recvbuffer.split(" ")[1].split(";")[0]
	self.__debug(self._status)
	if self._status == 'main:err':
	  self._url = None
	  self._event.set()
	
      if self._recvbuffer.startswith("STATE"):
	self._state = self._recvbuffer.split(" ")[1]
	self.__debug(self._state)
	
      if self._recvbuffer.startswith("START"):
	# Parse START
	self._url = self._recvbuffer.split(" ")[1]
	self._event.set()
	self.__debug(self._url)