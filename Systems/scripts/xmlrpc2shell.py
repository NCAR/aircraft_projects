#!/usr/bin/python

import SimpleXMLRPCServer, os
PORT=30009

def do_cmd(params):
        call= "gnome-terminal --window-with-profile=\"%s\" -t \"%s\" -x %s" % (params)
        #call= "xterm -hold -T \"%s\" -e \"%s\"" % (params)
        os.system(call)
        return 0

#The server object
class shell_com_server:
    def shell_exec(self, p,t,c):
        return do_cmd((p,t,c))

scs = shell_com_server()
serv = SimpleXMLRPCServer.SimpleXMLRPCServer(("localhost", PORT))
serv.register_instance(scs)

if (os.fork()==0):
    print "Listening on port %d"%(PORT)
    serv.serve_forever()

else:
    print 'Started xmlrpc2shell server'
