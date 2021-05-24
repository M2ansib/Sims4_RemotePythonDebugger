from HTML import HTML_STRING

from sims4.commands import *

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
from io import StringIO
from traceback import print_exc
import sys
from threading import Thread
import webbrowser

SERVER_PORT = 8080

_server		= None
_globals	= None

__author__ = "Mansib Miraj"
__copyright__ = u"© 2015-2021 Mansib Miraj, all rights reserved."
__credits__ = ["Mansib Miraj"]
__license__ = "GPLv3"
__version__ = "1.0.1"
__maintainer__ = "Mansib Miraj"
__email__ = "mansibmiraj@gmail.com"
__status__ = "Staging"

def is_eval_expression(string):
    try:
        compile(string, "bogusfile.py", "eval")
        return True
    except:
        return False

class IORerouteContext:
	def __init__(self,stdout,stderr):
		self._stdout	= stdout
		self._stderr	= stderr
		
		self._realStdout	= sys.stdout
		self._realStderr	= sys.stderr
		
	def __enter__(self):
		sys.stdout	= self._stdout
		sys.stderr	= self._stderr
		
		return self
		
	def __exit__(self,exceptionType,exception,traceback):
		sys.stdout	= self._realStdout
		sys.stderr	= self._realStderr
		
		return False

class ConsoleStderr:
	def __init__(self,out):
		self._out = out
		
	def write(self,value):
		self._out.write("<span class=\"Stderr\">{}</span>".format(value))
		
class CheatStdout:
	def __init__(self,_connection):
		self._output = CheatOutput(_connection)
		
	def write(self,value):
		# Strip trailing newline:
		if value[-1]=="\n":
			value = value[:-1]
		
		self._output(value)

class RequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path=="/":
				self._getRoot()
			else:
				self._getNotFound()
			
		except Exception as exception:
			self._exception(exception)
		
	def do_POST(self):
		try:
			if self.path!="/execute":
				return self._notFound()
			
			length	= int(self.headers["Content-Length"])
			data	= parse_qs(self.rfile.read(length).decode("utf-8"))
			code	= data.get("code",[None])[0]
			
			if not code:
				return self._error("No Code Received","Client didn't send any code to be executed to the server.")
			
			stdout = StringIO()
			stderr = ConsoleStderr(stdout)
			
			with IORerouteContext(stdout,stderr):
				try:
					if is_eval_expression(code):
						print(eval(code, _globals))
					else:
						exec(code, _globals)
				except Exception as exception:
					print_exc()
			
			if stdout.tell()==0:
				stdout.write("<span class=\"NoOutput\">*No Output*</span>")
				
			self.send_response(200)
			self.send_header("Content-Type","text/html")
			self.end_headers()
			
			self.wfile.write(stdout.getvalue().encode("utf-8"))
			
		except Exception as exception:
			self._exception(exception)
			
	def _getRoot(self):
		self.send_response(200)
		self.send_header("Content-Type","text/html")
		self.end_headers()
		
		self.wfile.write(HTML_STRING)
		
	def _exception(self,exception):
		stdout = StringIO()
		
		with IORerouteContext(stdout,stdout):
			print_exc()
			
		self._error(exception,stdout.getvalue())
		
	def _getNotFound(self):
		self.send_response(404)
		self.send_header("Content-Type","text/html")
		self.end_headers()
		
		self.wfile.write(b"<h1>404 Not Found</h1><p>Please ensure that you've entered the right URL before reloading the page.</p>")
			
	def _error(self,title,description):
		self.send_response(500)
		self.send_header("Content-Type","text/html")
		self.end_headers()
		
		self.wfile.write("<b>{}:</b>\n<pre>{}</pre>".format(title,description).encode("utf-8"))

@Command("pyremote.start",command_type = CommandType.Live)
def pythonConsoleStart(_connection = None):
	out = CheatStdout(_connection)
	
	with IORerouteContext(out,out):
		try:
			print("Starting Python console HTTP server...")
			
			global _server
			global _globals
			
			if _server!=None:
				print("Cannot start Python console server: server is already running")
				
				return
			
			_server		= HTTPServer(("",SERVER_PORT),RequestHandler)
			_globals	= {"_connection":_connection}
			
			Thread(target = _server.serve_forever).start()
			
			print("Serving Python console via HTTP at http://127.0.0.1:{}".format(SERVER_PORT))
			
			webbrowser.open("http://127.0.0.1:{}/".format(SERVER_PORT))
			
		except Exception as exception:
			print("!!! Unable to start Python console HTTP server: Python exception: !!!")
			
			print_exc()

@Command("pyremote.stop",command_type = CommandType.Live)
def pythonConsoleStop(_connection = None):
	out = CheatStdout(_connection)
	
	with IORerouteContext(out,out):
		try:
			print("Stopping Python console HTTP server...")
			
			global _server
			global _globals
			
			if _server==None:
				print("Cannot stop Python console HTTP server: server is not running")
				
				return
			
			_server.shutdown()
			
			_server		= None
			_globals	= None
			
			print("Python console HTTP server has been stopped.")
			
		except Exception as exception:
			print("!!! Unable to stop Python console HTTP server: Python exception: !!!")
			
			print_exc()
	
#_server		= HTTPServer(("",SERVER_PORT),RequestHandler)
#_globals	= {}

#Thread(target = _server.serve_forever).start()

import sims4.commands
import sims4.reload as r
import os.path
 
@sims4.commands.Command('reload', command_type=sims4.commands.CommandType.Live)
def reload_cmd(module:str, _connection=None):
    output = sims4.commands.CheatOutput(_connection)
    try:
        dirname = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(dirname, module) + ".py"
        output("Reloading {}".format(filename))
        reloaded_module = r.reload_file(filename)
        if reloaded_module is not None:
            output("Done reloading!")
        else:
            output("Error loading module or module does not exist")
    except BaseException as e:
        output("Reload failed: ")
        for v in e.args:
            output(v)