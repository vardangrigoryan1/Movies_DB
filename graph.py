from ds_collection import *
from indexing import *
from query_engine import *

class Graph:
    class Vertex:
        def __init__(self, element):
            self.element = element

        def __str__(self):
            return str(self.element)

        def __repr__(self):
            return str(self.element)

    class Edge:
        def __init__(self, u, v, weight=1):
            self.u = u
            self.v = v
            self.weight = weight

    def __init__(self):      
        # adjacency map: Vertex -> {Vertex: Edge}
        self.adj = {}

    def num_vertices(self):
        return len(self.adj)

    def vertices(self):
        return list(self.adj.keys())

    def num_edges(self):
        count = 0
        for v in self.adj:
            count += len(self.adj[v])
        return count

    def edges(self):
        edgelist = []
        for v in self.adj:
            for e in self.adj[v].values():
                edgelist.append(e)
        return edgelist

    # -------------- Access methods --------------
    def get_edge(self, u, v):
        if u in self.adj and v in self.adj[u]:
            return self.adj[u][v]
        return None

    def end_vertices(self, e):
        return (e.u, e.v)

    def opposite(self, u, e):
        if e.u == u:
            return e.v
        if e.v == u:
            return e.u
        return None

    def out_degree(self, u):
        return len(self.adj.get(u, {}))

    def in_degree(self, v):
        count = 0
        for u in self.adj:
            if v in self.adj[u]:
                count += 1
        return count

    def outgoing_edges(self, u):
        return list(self.adj.get(u, {}).values())

    def incoming_edges(self, v):
        incoming = []
        for u in self.adj:
            if v in self.adj[u]:
                incoming.append(self.adj[u][v])
        return incoming

    # -------------- Update methods --------------
    def insert_vertex(self, element):
        v = self.Vertex(element)
        if v not in self.adj:
            self.adj[v] = {}
        return v

    def insert_edge(self, u, v, weight=1):
        if u not in self.adj:
            self.adj[u] = {}
        if v not in self.adj:
            self.adj[v] = {}

        # if edge exists, increment weight
        if v in self.adj[u]:
            self.adj[u][v].weight += weight
        else:
            self.adj[u][v] = self.Edge(u, v, weight)

        return self.adj[u][v]

    def remove_edge(self, u, v):
        if u in self.adj and v in self.adj[u]:
            del self.adj[u][v]

    def remove_vertex(self, v):
        if v not in self.adj:
            return
        # remove incoming edges
        for u in self.adj:
            if v in self.adj[u]:
                del self.adj[u][v]
        del self.adj[v]


    # -------- BFS shortest path --------
    def shortest_path(self, src, dst):
        if src not in self.adj or dst not in self.adj:
            return None

        queue = [src]
        head = 0
        parent = {src: None}

        while head < len(queue):
            u = queue[head]
            head += 1

            for v in self.adj[u]:
                if v not in parent:
                    parent[v] = u
                    if v == dst:
                        # reconstruct path
                        path = [dst]
                        cur = dst
                        while parent[cur] is not None:
                            cur = parent[cur]
                            path.append(cur)
                        path.reverse()
                        return path
                    queue.append(v)

        return None

    # -------- Co-actor graph builder --------
    def add_coactors(self, actor_list):
        """
        actor_list = ["Actor A", "Actor B", "Actor C"]
        Adds edges between all pairs of actors in the movie.
        """
        verts = []
        for name in actor_list:
            verts.append(self.insert_vertex(name))

        for i in range(len(verts)):
            for j in range(i + 1, len(verts)):
                self.insert_edge(verts[i], verts[j], weight=1)
                self.insert_edge(verts[j], verts[i], weight=1)
