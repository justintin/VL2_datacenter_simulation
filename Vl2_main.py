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

vl2 = VL2agent() #instantiate a vl2 agent object

class Tutorial (object):

  def __init__ (self, connection):
   
    self.connection = connection

    connection.addListeners(self)
    
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
