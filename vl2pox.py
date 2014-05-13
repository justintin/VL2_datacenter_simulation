from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet import *
import pox.lib.packet as ppp
import struct
from pox.lib.packet.packet_base import packet_base
from pox.lib.packet.packet_utils import ethtype_to_str
from pox.lib.addresses import * 
log = core.getLogger()
from pox.lib.util import dpidToStr

from mininet.topo import Topo
from pox.openflow.of_json import *


class Path (object):
    counter  = 0
    def __init__ (self, steps):
        self.pathID = Path.counter
        self.startP = steps[0]
        self.endP = steps[len(steps)-1]
        self.cost = -1
        self.steps = steps
        self.usageOfLinks = {}
        
        Path.counter += 1

        #makes the dictionary for each link in the entire path and its cost
        #{31:{21:-1}}, to look up cost of link 31 to 22: self.usageOfLinks[31][22]
        for a in range(len(self.steps) - 1):
            self.usageOfLinks[steps[a]] = {steps[a+1]: -1}

        #this function is for sorting purposes:
        def __repr__ (self):
            return repr((self.cost))

    def display(self):
	print self.steps

class VL2agent(object):
    ########################################################################initial area
  agg_to_core = {21 : [11,  12 ], 22 : [11,  12 ], 23 : [11,  12 ], 24 : [11,  12 ] }
  tor_to_agg = {31: [21, 22] , 32: [21, 22], 33: [23, 24], 34: [23, 24] }
    
  core_to_agg = {11: [21, 22, 23, 24], 12 : [21, 22, 23, 24]}
  agg_to_tor = {21: [31, 32], 22: [31, 32], 23: [33, 34], 24: [33, 34]}
  #this will look like: {"31to32": [Path1, Path2, ..., Path8], "31to34":[Path1, Path2, ..., Path8], .....}
  src_dst_paths = {}

  (tor1,tor2,tor3,tor4)=range(31,35)
  (agg1,agg2,agg3,agg4)=range(21,25)
  (core1,core2)=range(11,13)
  (port1,port2,port3,port4)=range(1,5)
  
  link_cost = {31 : {21: -1, 22: -1}, 32 : {21: -1, 22: -1}, 33 : {23: -1, 24: -1}, 34 : {23: -1, 24: -1}, \
    21 : {11: -1, 12: -1, 31: -1, 32: -1}, 22 : {11: -1, 12: -1, 31: -1, 32: -1}, 23 : {11: -1, 12: -1, 33: -1, 34: -1}, \
    24 : {11: -1, 12: -1, 33: -1, 34: -1},11:{21: -1, 22: -1, 23: -1, 24: -1},12:{21: -1, 22: -1, 23: -1, 24: -1}}

  
  
  dpidtomac={31:EthAddr("00:00:00:00:00:01"),32:EthAddr("00:00:00:00:00:02"),33:EthAddr("00:00:00:00:00:03"),34:EthAddr("00:00:00:00:00:04")}

  iptomac={}
  iptoport={}
  iptodpid={IPAddr('255.255.255.255'):-1}

  port_switch={tor1:{port1:agg1,port2:agg2},tor2:{port1:agg1,port2:agg2},tor3:{port1:agg3,port2:agg4},tor4:{port1:agg3,port2:agg4},\
  agg1:{port1:core1,port2:core2,port3:tor1,port4:tor2},agg2:{port1:core1,port2:core2,port3:tor1,port4:tor2},\
  agg3:{port1:core1,port2:core2,port3:tor3,port4:tor4},agg4:{port1:core1,port2:core2,port3:tor3,port4:tor4},\
  core1:{port1:agg1,port2:agg2,port3:agg3,port4:agg4},core2:{port1:agg1,port2:agg2,port3:agg3,port4:agg4}}

  switch_port={tor1:{agg1:port1,agg2:port2},tor2:{agg1:port1,agg2:port2},tor3:{agg3:port1,agg4:port2},tor4:{agg3:port1,agg4:port2},\
  agg1:{core1:port1,core2:port2,tor1:port3,tor2:port4},agg2:{core1:port1,core2:port2,tor1:port3,tor2:port4},\
  agg3:{core1:port1,core2:port2,tor3:port3,tor4:port4},agg4:{core1:port1,core2:port2,tor3:port3,tor4:port4},\
  core1:{agg1:port1,agg2:port2,agg3:port3,agg4:port4},core2:{agg1:port1,agg2:port2,agg3:port3,agg4:port4}}
  steps = []
    
  for i in tor_to_agg:
    steps.append (i) #[31]
    for j in tor_to_agg[i]:
        steps.append(j) #[31, 21]
        for k in agg_to_core[j]:
            steps.append (k) #[31, 21, 11]
            for m in core_to_agg[k]:
                steps.append(m) #[31, 21, 11, 21]
                for q in agg_to_tor[m]:
                    if (q != i):
                        steps.append (q) #[31, 21, 11, 21, 32]
                        theString = str(steps[0]) + "to" + str(steps[len(steps)-1])
                        newList = steps[:]
                        path = Path (newList)

                        if theString in src_dst_paths:
                            #print "its here"
                            src_dst_paths[theString].append (path)                              
                        else:                              
                            src_dst_paths[theString] = []
                            src_dst_paths[theString].append(path) 
                            #print src_dst_paths[theString]
                        #print "right before delete"
                        #print steps  
                        
                        a = steps.pop()
                        #print src_dst_paths[theString][0].steps
                a = steps.pop()
            a = steps.pop()    
        a = steps.pop()
    a = steps.pop()

  def arp_reply(self, packet,packet_in, connection):
      arp_reply = arp()
      #arp_reply.hwsrc = self.torlookup[packet.payload.protodst]

      switchid = vl2.iptodpid[packet.payload.protodst]
      arp_reply.hwsrc = vl2.dpidtomac[switchid]
      arp_reply.hwdst = packet.src
      arp_reply.opcode = arp.REPLY
      arp_reply.protosrc =packet.payload.protodst
      #print packet.payload.protodst
      arp_reply.protodst = packet.payload.protosrc
      ether = ethernet() # ethernet header is added to sent it out further
      ether.type = ethernet.ARP_TYPE
      ether.dst = packet.src
      ether.src = arp_reply.hwsrc
      ether.set_payload(arp_reply)
      msg = of.ofp_packet_out(data = ether)
      msg.actions.append(of.ofp_action_output(port = packet_in.in_port))
      #print packet_in.in_port
      connection.send(msg)


vl2 = VL2agent() #instantiate a vl2 agent object

class Tutorial (object):



  def __init__ (self, connection):
   
    self.connection = connection

    connection.addListeners(self)


  def random_path (self, startP, endP ):
      #print startP, endP
      stringPoint = str (startP) + "to" + str (endP)
      #print stringPoint
      allPaths = vl2.src_dst_paths [stringPoint]
      #print allPaths[0].steps
      return allPaths[0]
                                          
  #takes the dpid's of the start (src) and end (dst) switches
  def choose_path (self, startP, endP):
      """ determines the best path between a start point and an end point """
      #a list of all the paths between two points
      stringPoint = str (startP) + "to" + str (endP)
      allPaths = vl2.src_dst_paths [stringPoint]

      #sort the paths according to their cost (cost) and then choose the first one in the sorted list as the least cost path
      sortedPathList = sorted(allPaths, key=lambda path: path.cost)
      leastCostPath = sortedPathList[0]
      return leastCostPath
  
  #this will set the cost of the path, based on the usage of the links inside the path, the cost of the path will be equal to the highest usage of its links
  def set_cost_of_path (self, path):
      costOfPath = -1
      for a in path.usageOfLinks:
          for b in path.usageOfLinks[a]:
              if costOfPath < path.usageOfLinks[a][b]:
                  costOfPath = path.usageOfLinks[a][b]

      path.cost = costOfPath

  #==================********************==================
                                                
  #we will need a function that determines and sets the usage of each link and stores it in self.link_cost
  def set_cost_of_links_of_path (self, path):
      ## links = {31: {21: -1}}
      for i in path.usageOfLinks:
          for j in path.usageOfLinks[i]:
              path.usageOfLinks[i][j] = vl2.link_cost[i][j]
      
  #==================********************==================
  def update_path_costs (self):
      for i in vl2.src_dst_paths:
          for j in vl2.src_dst_paths[i]:
              for path in self.src_dst_paths[i][j]:
                  self.set_cost_of_links_of_path (self, path)
                  self.set_cost_of_path (self, path)



  def installRules(self,packet, path):
      #choose a path, write a function to pick a path and return a stack with dpid
      #print "after+", path.steps
      p=path.steps[:]
      
      if p==[]:
         print "No patch chosen"
      prev = p[0] 
      del p[0]
      
      while p:
         next = p[0]
         del p[0]
         out_port = vl2.switch_port[prev][next]
         con = core.openflow.getConnection(prev)
         msg1=of.ofp_flow_mod()
         msg1.actions.append(of.ofp_action_output(port = out_port ))
         msg1.match = of.ofp_match.from_packet(packet)
         con.send(msg1)
         prev=next
      
  def rewrite(self,packet):
      msg=of.ofp_flow_mod()
      msg.actions.append(of.ofp_action_dl_addr.set_dst(vl2.iptomac[packet.payload.dstip]))
      msg.actions.append(of.ofp_action_output(port = vl2.iptoport[packet.payload.dstip]))
      msg.match = of.ofp_match.from_packet(packet)
      self.connection.send(msg)


     
  def vl2controller (self, packet, packet_in,event):
    
    	 
    if packet.type == packet.ARP_TYPE:
           if packet.payload.opcode == arp.REQUEST: 
              #if packet.payload.protosrc not in self.iptodpid:
              if not vl2.iptodpid.has_key(packet.payload.protosrc):
                 vl2.iptodpid[packet.payload.protosrc] = self.connection.dpid
                 vl2.iptomac[packet.payload.protosrc] = packet.src
                 vl2.iptoport[packet.payload.protosrc] = packet_in.in_port
                 #print packet.payload.protosrc
		 #print vl2.iptodpid[packet.payload.protosrc]
		 #print vl2.iptomac[packet.payload.protosrc]
		 #print vl2.iptoport[packet.payload.protosrc]
              else:
                try:
                  vl2.arp_reply(packet,packet_in,self.connection)
                  
                except Exception:
                  print "arp exception"
           else:
	      pass
    else:
      if packet.find('ipv4') :
           if packet.payload.dstip != IPAddr('255.255.255.255'):  # we are forbidden boardcast because vl2 agent will take care of that
                 if self.connection.dpid == vl2.iptodpid[packet.payload.dstip]: 
                    self.rewrite(packet)
                 else:
                     if packet.find('tcp'):
                       
                          path = self.choose_path(self.connection.dpid, vl2.iptodpid[packet.payload.dstip])
        	          self.installRules(packet, path)
                        
                     else:
                        
                          path = self.random_path(self.connection.dpid, vl2.iptodpid[packet.payload.dstip])
                          
                          #print "before+", path.steps
                          self.installRules(packet, path)
                         
               
		
  def _handle_PacketIn (self, event):
   
    packet = event.parsed 
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp 
    self.vl2controller(packet, packet_in,event)
########################################################
def _timer_func ():
  for connection in core.openflow._connections.values():
    #print connection.dpid
    connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
    connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))
  log.debug("Sent %i flow/port stats request(s)", len(core.openflow._connections))

# handler to display flow statistics received in JSON format
# structure of event.stats is defined by ofp_flow_stats()
def _handle_flowstats_received (event):
  stats = flow_stats_to_list(event.stats)
  #ppp=event.parsed
  print event.dpid
  #print ppp.payload.srcip
  #print ppp.src
  #print event.ofp.in_port
  log.debug("FlowStatsReceived from %s: %s", 
    dpidToStr(event.connection.dpid), stats)

  # Get number of bytes/packets in flows for web traffic only
  web_bytes = 0
  web_flows = 0
  web_packet = 0
  for f in event.stats:
    if f.match.tp_dst or f.match.tp_src:
      web_bytes += f.byte_count
      web_packet += f.packet_count
      web_flows += 1
      #print f.match.nw_src, f.match.nw_dst,f.match.tp_src,f.match.tp_dst

      #######################################
      try:
        snum=event.connection.dpid
        self.link_cost[snum][self.port_switch[snum][in_port]]= byte_count/5
      except Exception:
          pass
      ##############################################

  log.info("Web traffic from %s: %s bytes (%s packets) over %s flows", 
    dpidToStr(event.connection.dpid), web_bytes, web_packet, web_flows)
      
# handler to display port statistics received in JSON format
def _handle_portstats_received (event):
  stats = flow_stats_to_list(event.stats)
  log.debug("PortStatsReceived from %s: %s", 
    dpidToStr(event.connection.dpid), stats)
######################################################


def launch ():
  """
  Starts the component
  """
  from pox.lib.recoco import Timer

  # attach handsers to listners
  
  core.openflow.addListenerByName("FlowStatsReceived", 
    _handle_flowstats_received) 
  core.openflow.addListenerByName("PortStatsReceived", 
    _handle_portstats_received) 

  # timer set to execute every five seconds
  Timer(1, _timer_func, recurring=True)
  
  def start_switch (event):
    #print event.__class__
    log.debug("Controlling %s" % (event.connection,))

    Tutorial(event.connection)
    
  core.openflow.addListenerByName("ConnectionUp", start_switch)
