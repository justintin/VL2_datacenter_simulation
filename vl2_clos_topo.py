"""Custom topology example
Adding the 'topos' dict with a key/value pair to generate our newly defined
"""

from mininet.topo import Topo


class MyTopo(Topo):

#   creat servers and switches
    def  CreatTopo(self,Da,Di,**params):
         Topo.__init__(self,**params)
         inters = [self.addSwitch('inter%x' % k,dpid='%x' %(k+10))
                   for k in range(1,Da/2+1)  ]
         aggs = [self.addSwitch('agg%x' % k,dpid='%x' %(k+20))
                  for k in range(1,Di+1)  ]
         tors = [self.addSwitch('tor%x' % k,dpid='%x' %(k+30))
                  for k in range(1,Da*Di/4+1)  ]
         hosts = [ self.addHost( 'vm%d' % i,ip='10.0.0.%d' %i )
                    for i in range(1,(Da*Di/4)*3+1)  ]

# creat links between instances
         for a in aggs:
            for i in inters:
               self.addLink(a,i)
            
         for i in range(0,Di/2):
            for j in range(0,Da*Di/8):       
               self.addLink(aggs[i],tors[j])

         for i in range(Di/2,Di):
            for j in range(Da*Di/8,Da*Di/4):
               self.addLink(aggs[i],tors[j])

         for i in range(0,Da*Di/4):
             self.addLink(hosts[i*3],tors[i])
	     self.addLink(hosts[i*3+1],tors[i])
             self.addLink(hosts[i*3+2],tors[i])
         print self.ports
# configure network paramaters
 
    def __init__(self,Da=1,Di=1,**params):
       self. CreatTopo(Da,Di)


topos = { 'mytopo': ( lambda: MyTopo(4,4)) }
