import collections

class Vertex:
    """A generic graph vertex with an adjacency list."""

    def __init__(self, value):
        self.value = value
        # Use an ordered dict so that the order in which the edges are
        # traversed is deterministic
        self._edges = collections.OrderedDict()

    def add_edge(self, vertex_to):
        self.add_edge_object(self.Edge(self, vertex_to))

    def add_edge_object(self, edge):
        self._edges[edge.vertex_to] = edge

    @property
    def outgoing_edges(self):
        return self._edges.values()

    def __hash__(self):
        return hash(id(self))

    class Edge:

        def __init__(self, vertex_from, vertex_to):
            self.vertex_from = vertex_from
            self.vertex_to = vertex_to

        def copy(self):
            return Vertex.Edge(self.vertex_from, self.vertex_to)

class ShortestPathsVertex(Vertex):
    """A graph vertex with some extra scratch space for Dijkstra's
    algorithm."""

    def __init__(self, value):
        super().__init__(value)
        self.length = None
        self.parent_edge = None

    def add_edge(self, vertex_to, weight):
        self.add_edge_object(self.Edge(self, vertex_to, weight))

    def create_copy(self):
        return Vertex(self.value)

    def reversed_path_edges(self):
        vertex = self
        while vertex.parent_edge is not None:
            yield vertex.parent_edge
            vertex = vertex.parent_edge.vertex_from

    class Edge(Vertex.Edge):

        def __init__(self, vertex_from, vertex_to, weight):
            super().__init__(vertex_from, vertex_to)
            self.weight = weight

class Heap:
    """An uncomplicated implementation of the heap data structure utilized by
    Dijkstra's algorithm. This has abysmal remove-min performance. Don't try
    this at home, kids."""

    def __init__(self):
        self.values = {}

    def insert(self, value, key):
        """Constant time complexity."""
        self.values[value] = key

    def remove_min(self):
        """Linear time complexity."""
        value, key = min(self.values.items(), key=lambda p: p[1])
        del self.values[value]
        return value, key

    def decrease_key(self, value, new_key):
        """Constant time complexity."""
        self.values[value] = new_key

    def __len__(self):
        return len(self.values)

def compute_shortest_paths(source_vertex, destination_vertices, zero=0):
    """An implementation of Dijkstra's algorithm with time complexity
    O(V^2 + E).
    
    After this procedure finishes, the vertices of the graph will have their
    shortest path metadata filled in. Note that the resulting sub-graph of
    shortest paths will always be a tree."""
    source_vertex.length = zero
    heap = Heap()
    heap.insert(source_vertex, zero)
    completed = set()
    unseen_dests = set(destination_vertices)
    while heap and unseen_dests:
        u, length = heap.remove_min()
        completed.add(u)
        unseen_dests.discard(u)
        for edge in u.outgoing_edges:
            v = edge.vertex_to
            new_length = length + edge.weight
            if v.length is None:
                v.length = new_length
                v.parent_edge = edge
                heap.insert(v, new_length)
            elif v not in completed and new_length < v.length:
                v.length = new_length
                v.parent_edge = edge
                heap.decrease_key(v, new_length)
    return completed

def construct_shortest_paths_subtree(source_vertex, destination_vertices):
    """Follow the shortest-paths backpointers and construct the corresponding
    sub-tree. Return the root vertex of the tree."""
    # Once we encounter a vertex we have already seen, we can stop following
    # the backpointers, since that branch of the tree has already been
    # traversed. Hence the continue and break statements.
    vertex_copies = {}
    for vertex in destination_vertices:
        vertex_to = vertex_copies.get(vertex)
        if vertex_to is None:
            vertex_to = vertex_copies[vertex] = vertex.create_copy()
        else:
            continue
        for edge in vertex.reversed_path_edges():
            vertex_from = vertex_copies.get(edge.vertex_from)
            if vertex_from is None:
                vertex_from = vertex_copies[edge.vertex_from] = edge.vertex_from.create_copy()
                vertex_from.add_edge_object(edge.create_copy(vertex_from, vertex_to))
                vertex_to = vertex_from
            else:
                vertex_from.add_edge_object(edge.create_copy(vertex_from, vertex_to))
                break
    root = vertex_copies.get(source_vertex)
    if root is None:
        root = source_vertex.create_copy()
    return root

def preorder_traversal(root_vertex):
    """Do a pre-order traversal of the vertices of a tree."""
    yield root_vertex
    for edge in root_vertex.outgoing_edges:
        for vertex in preorder_traversal(edge.vertex_to):
            yield vertex

def depth_first_traversal(root_vertex):
    """Do a depth-first traversal of the vertices in a graph."""
    queued = { root_vertex }
    agenda = [root_vertex]
    while agenda:
        vertex = agenda.pop()
        yield vertex
        for edge in vertex.outgoing_edges:
            if edge.vertex_to not in queued:
                queued.add(edge.vertex_to)
                agenda.append(edge.vertex_to)
