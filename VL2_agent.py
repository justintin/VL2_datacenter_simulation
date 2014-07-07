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