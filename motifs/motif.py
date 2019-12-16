import struct 



class SubGraph(object):
    def __init__(self, vertices, edges):
        self.vertices = vertices
        self.edges = edges



class Motif(object):
    def __init__(self, trace, nodes, motif_index):
        """
        Initialize a motif obejct for a trace and a given set of nodes. A motif
        is a frequently occuring set of nodes that appear in a graph.
        @params trace: the trace corresponding to this motif
        @params nodes: a list of nodes belonging to this motif
        @params motif_index: a unique identifier for this particular subgraph type
        """
        self.trace = trace
        self.nodes = nodes
        self.motif_index = motif_index

        # find the minimum and maximum timestamp for this motif
        self.minimum_timestamp = self.nodes[0].timestamp
        self.maximum_timestamp = self.nodes[0].timestamp
        for node in self.nodes:
            if node.timestamp < self.minimum_timestamp:
                self.minimum_timestamp = node.timestamp
            if node.timestamp > self.maximum_timestamp:
                self.maximum_timestamp = node.timestamp

        # get the duration for this motif
        self.duration = self.maximum_timestamp - self.minimum_timestamp

    def __lt__(self, other):
        """
        Custom operator to sort motifs first by the size of the motif and
        second by the start of the motif.
        @params other: the other motif to compare to
        """
        # this motif is larger than the other
        if len(self.nodes) < len(other.nodes): return True
        elif len(self.nodes) > len(other.nodes): return False
        # or it has a later timestamp
        elif self.minimum_timestamp > other.minimum_timestamp: return True
        else: return False

    def size(self):
        """
        Return the size of this motif based only on the number of nodes
        """
        return len(self.nodes)



def WriteMotifs(filename, motifs):
    """
    Write all of the found motifs for this trace to file.
    @params filename: the file to store the motifs
    @params motifs: a list of motif objects to save to disk
    """
    with open(filename, 'wb') as fd:
        nmotifs = len(motifs)
        fd.write(struct.pack('q', nmotifs))
        for motif in motifs:
            nnodes = len(motif.nodes)
            fd.write(struct.pack('q', nnodes))
            for node in motif.nodes:
                fd.write(struct.pack('q', node.index))
            fd.write(struct.pack('q', motif.motif_index))
