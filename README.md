JSON-RPC for python
===================
This is a modern fork of the JSON-RPC implementation originally
hosted on [json-rpc.org](http://json-rpc.org/wiki/python-json-rpc).
It has been updated for modern versions of Python.

jsonrpc implements the
[JSON-RPC 2.0 specification](http://www.jsonrpc.org/spec.html).

The mod_python and CGI service handlers are backwards compatible
with JSON-RPC 1.0 clients.

Requirements
------------
Python 2.6+ is natively supported.
Python 2.5 requires the 'simplejson' module.

The 'simplejson' module enables some speedups not present
in python2.6's 'json' module.  You may want to install it
if you are using python2.6.

Using the ServiceProxy class
----------------------------
If everything worked you should now be able to call JSON-RPC services.
Start your favorite python shell and enter the code below:

    >>> from jsonrpc import ServiceProxy
    >>> s = ServiceProxy('http://www.raboof.com/projects/jayrock/demo.ashx')
    >>> print s.echo('foobar')

The example above creates a proxy object for a service hosted on raboof.com.
It calls the service's echo method and prints out the result of the call.

This implementation supports JSON-RPC 2.0 which means that either
positional arguments or keyword arguments, but not both, are allowed.


Creating CGI based services
---------------------------
To provide your own service you can create a python CGI-Script and use
jsonrpc's handleCGI method for handling requests.

    #!/usr/bin/env python
    
    from jsonrpc import handleCGI, servicemethod
    
    @servicemethod
    def echo(msg):
        return msg
    
    
    if __name__ == '__main__':
        handleCGI()

This is the simplest way to create a service using a CGI script.
All methods in the script decorated using the `servicemethod` decorator
are available to remote callers.  All other methods are inaccessible
to the "outside world".

handleCGI() gives you some flexibility to define what to use as the service.
By default, as seen above it uses the __main__ module as a service.
You can though, specify a particular service to be used by passing it to
handleCGI(service) as first parameter:

    #!/usr/bin/env python
    
    from jsonrpc import handleCGI, servicemethod
    
    class MyService(object):
        @servicemethod
        def echo(self, msg):
            return msg
    
    
    if __name__ == '__main__':
        service = MyService()
        handleCGI(service)

Creating mod-python based services
----------------------------------
Similar to the way the CGI handling works, you can use jsonrpc's
mod-python handler. First you need to install and setup mod-python
to handle service URLs using jsonrpc's mod-python handler.
E.g. in your .htaccess file in any folder that is being served by apache add:

    AddHandler mod_python .py
    PythonHandler jsonrpc

Make sure Apache is setup to allow you to add the AddType Directive in
.htaccess files. Alternatively you can create an apache config file which
gets loaded by apache upon startup. In a Location or Directory section you
should add the python handler:

    Alias /services/ /var/www/json-rpc-services/
    <Location /services/>
        AddHandler mod_python .py
        PythonHandler jsonrpc
    </Location>

If you have not installed jsonrpc using it's setup script, you will need to
add it's location to python's sys-path so that mod-python can find it.
In your apache config or .htaccess file add:

    ...
    PythonHandler jsonrpc
    PythonPath "sys.path+['/path/to/where/jsorpc/package/is/located/']"

Now you need to create a python script that will be used as a service.
Place it in a sub folder that is covered by the Directives above.
E.g. in the folder of where .htaccess is located or a subfolder thereof or in
any sub-folder of /var/www/json-rpc-services/ for the second config example.

Similar to the CGI based service you can create a script with methods
decorated using the `servicemethod` decorator:

    from jsonrpc import handleCGI, servicemethod
    
    @servicemethod
    def echo(msg):
        return msg

Again, this is probably the simplest way to create a service.

You can also create a script which exposes a service, which will then be
used as the service.

    from jsonrpc import servicemethod
    
    class MyService(object):
        @servicemethod
        def echo(self, msg):
            return msg
    
    service = MyService()

or you create a script which exposes a Service class. A service object
will be created using this class and used as a service.

    from jsonrpc import servicemethod
    
    class Service(object):
        @servicemethod
        def echo(self, msg):
            return msg

Testing your services
---------------------
Lets assume you created a mod-python based or a CGI based service using a
script called test.py and that that script can be found under the URL
http://localhost/services/test.py (check your web server configuration).

Now you should be able to use your services with any JSON-RPC client
that supports json-rpc over HTTP. The simplest way to try it out, is to
start your python shell an use jsonrpc's ServiceProxy class.

    >>> from jsonrpc import ServiceProxy
    >>> s = ServiceProxy('http://localhost/services/test.py')
    >>> print s.echo('foobar')

Error handling
--------------
Any error that the ServiceProxy received through the JSON-RPC protocol
will be raised as a JSONRPCException before the called method returns.

The exception raised will contain a service specific error object,
which can be accessed using the exception's error property.

    try:
        print s.echo('foobar')
    except JSONRPCException, e:
        print repr(e.error)

Any exception raised in a Service's method during invokation will be
converted into an error object and transmitted back to the caller by jsonrpc. The error object will use the exception's class name as a name property and it's message property as the message property of the error object being returned.
