from mininet.topo import Topo

class CustomTopo(Topo):
    def build(self):
        # Create hosts
        h1 = self.addHost('h1', ip='10.0.0.1')
        h2 = self.addHost('h2', ip='10.0.0.2')
        h3 = self.addHost('h3', ip='10.0.0.3')
        
        # Create switch
        s1 = self.addSwitch('s1')
        
        # Add links between hosts and switch
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)

topos = {'custom_topo': (lambda: CustomTopo())}