HTML_STRING = rf"""
<html>
	<head>
		<title>TS4 Console</title>
		<style type="text/css">
			html,
			body
			{{
				margin: 0px;
				padding: 0px;
			}}

			* {{
				color: white;
				background-color: black !important;
			}}
			
			body
			{{
				background-color: #000;
				font-family: sans-serif;
			}}
			
			textarea#code
			{{
				width: 100%;
				height: 10rem;
				
				position: fixed;
				bottom: 0px;
			}}
			
			div#main
			{{
				padding: 0.5rem;
			}}
			
			div#output
			{{
				padding: 0.25rem;
				margin-bottom: 10.5rem;
				display: none;
			}}
			
			span.Stderr
			{{
				color: red !important;
				font-weight: bold !important;
			}}
			
			pre.CommandOutput
			{{
				background-color: #f5f5f5;
				padding: 0.25rem;
				margin-bottom: 0.25rem;
			}}
			
			pre.CommandOutput:first-child
			{{
				border-top: none;
			}}
			
			span.NoOutput
			{{
				font-style: italic;
			}}

			html {{
				background-color: #000000 !important;
			}}
			html, body, input, textarea, select, button {{
				background-color: #000000;
			}}
			html, body, input, textarea, select, button {{
				border-color: #6d614d;
				color: #ffffff;
			}}
			a {{
				color: #0d9aff;
			}}
			table {{
				border-color: #3e494d;
			}}
			::placeholder {{
				color: #cbc1b2;
			}}
			input:-webkit-autofill,
			textarea:-webkit-autofill,
			select:-webkit-autofill {{
				background-color: #404900 !important;
				color: #ffffff !important;
			}}
			::-webkit-scrollbar {{
				background-color: #000000;
				color: #c1b6a6;
			}}
			::-webkit-scrollbar-thumb {{
				background-color: #282f34;
			}}
			::-webkit-scrollbar-thumb:hover {{
				background-color: #434d53;
			}}
			::-webkit-scrollbar-thumb:active {{
				background-color: #2c353a;
			}}
			::-webkit-scrollbar-corner {{
				background-color: #000000;
			}}
			::selection {{
				background-color: #0034bf !important;
				color: #ffffff !important;
			}}
			::-moz-selection {{
				background-color: #0034bf !important;
				color: #ffffff !important;
			}}
		</style>
	</head>
	<body>
		<div id="main">
			<h1>TS4 Console</h1>
			<p>© 2015-2021 Mansib Miraj, all rights reserved.</p>
			<div id="output"></div>
		</div>
		<textarea id="code"></textarea>
		<script type="text/javascript">
			'use strict';
			
			let UP		= -1;
			let DOWN	= 1;
			
			let HELLO_WORLD = "import sys; print('[INFO] Embedded Python interpreter successfully. \\n[INFO] Python {{}} running on {{}}.\\n[INFO] Type your command into the text box below and press Control+Enter to invoke it.\\n[INFO] Use Control+Up and Control+Down to cycle through the command history.\\n[WARN] To prevent save corruption due to Maxis\\' faulty save serialization algorithm, it is\\n[WARN] advisable to create a new save file instead of overwriting an existing save.'.format(sys.version,sys.platform))";
			
			let output	= document.getElementById("output");
			let code	= document.getElementById("code");
			
			let history			= [];
			let historyIndex	= null;
			
			function execute(code,then)
			{{
				let request = new XMLHttpRequest();
				
				request.addEventListener("readystatechange",(event) => {{
					if (request.readyState!=4)
						return;
						
					output.style.display = "block";
					
					// Create a new element to hold the response:
					let out = document.createElement("pre");
					
					out.className = "CommandOutput";
					
					out.innerHTML+=request.responseText;
					
					output.appendChild(out);
					
					historyPush(code);
					
					if (then)
						then();
				}});
				
				let data = ("code="+encodeURIComponent(code));
				
				request.open("POST","/execute",true);
				request.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
				request.setRequestHeader("Content-Length",data.size);
				request.send(data);
			}}
			
			function historyTraverse(direction)
			{{
				if (history.length==0)
					return;
				
				if (historyIndex==null)
				{{
					historyIndex = ((direction==UP)? (history.length-1):0);
					
					code.value = history[historyIndex];
					
					return;
				}}
				
				historyIndex = (((historyIndex+direction) % history.length));
				
				if (historyIndex<0)
					historyIndex += history.length;
				
				code.value = history[historyIndex];
			}}
				
			function codeExecute()
			{{
				execute(code.value,() => {{
					code.value = "";
				
					window.scrollTo(0,document.body.scrollHeight);
				}});
			}}
			
			function codeIndent()
			{{
				let start = code.selectionStart;
				
				let first	= code.value.substr(0,start);
				let last	= code.value.substr(code.selectionEnd);
				
				if (code.selectionEnd==start)
				{{
					// Insert tab at cursor position:
					code.value = (first+"\t"+last);
					
					code.selectionStart	= (start+1);
					code.selectionEnd	= code.selectionStart;
				}}
				else
				{{
					// Indent entire selection:
					code.value = (first+"\t"+code.value.substr(start,code.selectionEnd).replace(/\n/g,"\n\t")+last);
					
					code.selectionStart	= start;
				}}
			}}
			
			function historyPush(value)
			{{
				history.push(value);
				
				historyIndex = null;
			}}
			
			code.addEventListener("keydown",(event) => {{
				switch (event.keyCode)
				{{
					case 13: // Enter
					{{
						if (!event.ctrlKey)
							return;
							
						// Ctrl+Enter was pressed. Execute code:
						event.preventDefault();
						
						codeExecute();
						
						return;
					}}
						
					case 38: // Up
					{{
						if (!event.ctrlKey || history.length==0)
							return;
						
						// Ctrl+Up was pressed. Navigate upward in the code history:
						event.preventDefault();
						
						historyTraverse(-1);
						
						return;
					}}
						
					case 40: // Down
					{{
						if (!event.ctrlKey || history.length==0)
							return;
						
						// Ctrl+Down was pressed. Navigate forward in the code history:
						event.preventDefault();
						
						historyTraverse(1);
						
						return;
					}}
						
					case 9: // Tab
					{{
						event.preventDefault();
						
						// TODO: Unindent when shift key is pressed?
						
						codeIndent();
						
						return;
					}}
				}}
			}});
			
			// Once everything is loaded, execute the "hello, world" code:
			window.addEventListener("load",(event) => {{
				execute(HELLO_WORLD);
				history.length = 0; // Remove the initialization code from history.
			}});
		</script>
	</body>
</html>
""".encode("utf-8")
