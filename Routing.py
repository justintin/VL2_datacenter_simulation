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