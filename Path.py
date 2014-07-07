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