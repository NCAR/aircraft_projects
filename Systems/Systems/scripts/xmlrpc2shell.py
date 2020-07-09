#!/usr/bin/python

import SimpleXMLRPCServer, os
PORT=30009

def do_cmd(params):
    call= "gnome-terminal --window-with-profile=\"%s\" -t \"%s\" -x %s " % (params)
    os.system(call)

#The server object
class shell_com_server:
    def shell_exec(self, p,t,c):

	if (os.forkpty()[0] == 0):
            do_cmd((p,t,c))

	else:
            return "Launched %s"%(c)

scs = shell_com_server()
serv = SimpleXMLRPCServer.SimpleXMLRPCServer(("localhost", PORT))
serv.register_instance(scs)

if (os.fork()==0):
    print "Listening on port %d"%(PORT)
    serv.serve_forever()

else:
    print 'Started xmlrpc2shell server'
