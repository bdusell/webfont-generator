import operator
import collections

from . import graph
from .operations import (copy_file, convert_with_fontforge, convert_with_sfntly,
    convert_with_woff2_compress, convert_with_woff2_decompress)
from .error import Error

FORMATS = ['ttf', 'otf', 'svg', 'eot', 'woff', 'woff2']
FORMATS_SET = set(FORMATS)

class ShortestPathsVertex(graph.ShortestPathsVertex):

    def create_copy(self):
        return TreeVertex(self.value)

    def add_edge(self, vertex_to, weight, file):
        self.add_edge_object(self.Edge(self, vertex_to, weight, file))

    class Edge(graph.ShortestPathsVertex.Edge):

        def __init__(self, vertex_from, vertex_to, weight, file):
            super().__init__(vertex_from, vertex_to, weight)
            self.file = file

        def create_copy(self, vertex_from, vertex_to):
            return ShortestPathsVertex.Edge(
                vertex_from, vertex_to, self.weight, self.file)

class TreeVertex(graph.Vertex):

    def __init__(self, operation):
        super().__init__(operation)
        # Use an ordered dict so that the order in which the edges are
        # traversed is deterministic
        self._incoming_edges = collections.OrderedDict()

    def add_edge_object(self, edge):
        super().add_edge_object(edge)
        edge.vertex_to._incoming_edges[self] = edge

    @property
    def incoming_edges(self):
        return self._incoming_edges.values()

    def process(self, logger):
        input_files = (e.file for e in self.incoming_edges)
        output_files = (e.file for e in self.outgoing_edges)
        self.value(input_files, output_files, logger)

class Vector:
    """Simple vector class for lexicographically orderable edge weights."""

    def __init__(self, x, y, z):
        self.value = (x, y, z)

    def __add__(self, other):
        value = map(lambda p: operator.add(*p), zip(self.value, other.value))
        return Vector(*value)

    def __lt__(self, other):
        return self.value < other.value

Vertex = ShortestPathsVertex

def noop(input_files, output_files, logger):
    pass

def make_file_dicts(input_files, output_dir):
    # Use the first input file to determine the names for the output files
    input_files = list(input_files)
    input_files_dict = { f.format : f for f in input_files }
    output_files_dict = {
        f : input_files[0].moved_and_converted_to(output_dir, f)
        for f in FORMATS }
    return input_files_dict, output_files_dict

def construct_dependency_graph(input_files_dict, output_files_dict):
    """Construct the dependency graph which describes which programs can be
    used to convert which files."""
    # Create a super-source vertex
    source_vertex = Vertex(noop)
    # Create a vertex for every possible input format
    input_vertices = { f : Vertex(noop) for f in FORMATS }
    # For every input file, connect the super-source to the appropriate input
    # vertex
    # Sort the input file formats first so that their order is deterministic
    input_file_formats = sorted(input_files_dict.keys())
    for f in input_file_formats:
        source_vertex.add_edge(input_vertices[f], Vector(0, 0, 0), None)
    # Create a vertex for every possible output
    output_vertices = { f : Vertex(noop) for f in FORMATS }
    # For every format, allow an output file to be copied from an input file
    # in the same format
    for f in FORMATS:
        copy_vertex = Vertex(copy_file)
        if f in input_files_dict:
            input_vertices[f].add_edge(
                copy_vertex, Vector(0, 0, 0), input_files_dict[f])
        copy_vertex.add_edge(
            output_vertices[f], Vector(0, 0, 1), output_files_dict[f])
    # FontForge can convert any one of ttf, otf, woff, svg to any of ttf, otf,
    # svg
    fontforge_vertex = Vertex(convert_with_fontforge)
    for f in ('ttf', 'otf', 'woff', 'svg'):
        if f in input_files_dict:
            input_vertices[f].add_edge(
                fontforge_vertex, Vector(0, 0, 0), input_files_dict[f])
        output_vertices[f].add_edge(
            fontforge_vertex, Vector(0, 0, 0), output_files_dict[f])
    for f in ('ttf', 'otf', 'svg'):
        fontforge_vertex.add_edge(
            output_vertices[f], Vector(1, 0, 0), output_files_dict[f])
    # sfntly can convert ttf to any of woff, eot
    sfntly_vertex = Vertex(convert_with_sfntly)
    if 'ttf' in input_files_dict:
        input_vertices['ttf'].add_edge(
            sfntly_vertex, Vector(0, 0, 0), input_files_dict['ttf'])
    output_vertices['ttf'].add_edge(
        sfntly_vertex, Vector(0, 0, 0), output_files_dict['ttf'])
    for f in ('woff', 'eot'):
        sfntly_vertex.add_edge(
            output_vertices[f], Vector(0, 1, 0), output_files_dict[f])
    # woff2_compress can convert ttf to woff2
    # Note that it requires the input file to be in the destination directory
    woff2_compress_vertex = Vertex(convert_with_woff2_compress)
    output_vertices['ttf'].add_edge(
        woff2_compress_vertex, Vector(0, 0, 0), output_files_dict['ttf'])
    woff2_compress_vertex.add_edge(
        output_vertices['woff2'], Vector(0, 1, 0), output_files_dict['woff2'])
    # woff2_decompress can convert woff2 to ttf
    woff2_decompress_vertex = Vertex(convert_with_woff2_decompress)
    output_vertices['woff2'].add_edge(
        woff2_decompress_vertex, Vector(0, 0, 0), output_files_dict['woff2'])
    woff2_decompress_vertex.add_edge(
        output_vertices['ttf'], Vector(0, 1, 0), output_files_dict['ttf'])
    # Return the super-source and output vertices
    return source_vertex, output_vertices

def convert_files(input_files, output_dir, output_formats, logger):
    # Construct the conversion dependency graph
    input_files_dict, output_files_dict = make_file_dicts(
        input_files, output_dir)
    source_vertex, output_vertices = construct_dependency_graph(
        input_files_dict, output_files_dict)
    # Sort the output formats so that their order is deterministic
    output_formats = sorted(output_formats)
    destination_vertices = [output_vertices[f] for f in output_formats]
    # Compute the shortest paths from the super-source vertex to the vertices
    # corresponding to each of the requested output formats
    reachable_vertices = graph.compute_shortest_paths(
        source_vertex, destination_vertices, Vector(0, 0, 0))
    # Raise an error if any of the output formats cannot be generated
    unreachable_vertices = set(destination_vertices) - reachable_vertices
    if unreachable_vertices:
        unreachable_files = sorted({
            e.file.full_path
            for v in unreachable_vertices
            for e in v.outgoing_edges })
        raise Error('unable to generate the following files: %s' % ' '.join(
            unreachable_files))
    # Follow the shortest-paths backpointers and construct a dependency sub-tree
    dependency_tree = graph.construct_shortest_paths_subtree(
        source_vertex, destination_vertices)
    # Execute the tasks in topological order
    for vertex in graph.preorder_traversal(dependency_tree):
        vertex.process(logger)
    # Return the output file objects
    return { f : output_files_dict[f] for f in output_formats }
