#-*- coding: utf-8 -*-


class Graph(object):
  def __init__(self, vertexes=None, edges=None):
    if not vertexes: vertexes = []
    if not edges: edges = []
    self._vertex = vertexes
    self._edge = edges
    if self._edge:
      self.remove_imaginary_edge()

  def remove_imaginary_edge(self):
    for fromVertex in self._vertex:
      for toVertex in self._vertex:
        edge = self.get_edge(fromVertex, toVertex)
        if not fromVertex == toVertex and edge:
          time = fromVertex.data._startArrive + fromVertex.data._taskTime + edge.length
          if time > toVertex.data._endArrive:
            self._edge.remove(edge)

  def add_vertex(self, vertex):
    self._vertex.append(vertex)
    for edge in vertex.edges:
      if not ({edge.beginVertex, edge.endVertex} - set(self._vertex)):
        self._edge.append(edge)
    self._edge = list(set(self._edge))

  def add_edge(self, edge):
    if edge.is_valid():
      self._edge.append(edge)

  def remove_vertex(self, vertex):
    if vertex in self._vertex:
      vertex.isValid = False
      self._vertex.remove(vertex)
      begin = []
      end = []
      for e in reversed(self._edge):
        if vertex in (e.beginVertex, e.endVertex):
          if vertex == e.beginVertex:
            end.append(e.endVertex)
          if vertex == e.endVertex:
            begin.append(e.beginVertex)
          self._edge.remove(e)
      for b in begin:
        for e in end:
          edge = self.get_edge(b, e)
          if b <> e and edge and not edge in self._edge:
            self._edge.append(edge)


  def remove_edge(self, edge):
    if edge in self._edge:
      self._edge.remove(edge)

  def remove_edge(self, index):
    if index < len(self._edge):
      self._edge.remove(self._edge[index])

  def get_vertex(self, index):
    if index < self.get_vertex_count():
      return self._vertex[index]
    else:
      return self._vertex[-1]

  def get_edge(self, begin, end):
    if not begin == end and not ({begin, end} - set(self._vertex)):
      for edge in begin.outEdge:
        if edge.endVertex == end:
          return edge
    return None

  def get_vertex_count(self):
    return len(self._vertex)

  def get_edge_count(self):
    return len(self._edge)

  def __iter__(self):
    for vertex in self._vertex:
      yield vertex


class Vertex(object):
  def __init__(self, data=None, outEdges=None, inEdges=None, coordinate=None):
    if not outEdges: outEdges = []
    if not inEdges: inEdges = []
    if not coordinate: coordinate = ()
    self.__coord = coordinate
    self.__inEdge = inEdges
    self.__outEdge = outEdges
    self.isValid = True
    self.__allEdge = self.__inEdge + self.__outEdge
    self.__data = data

  def __eq__(self, other):
    return self.data == other.data if other else False

  def __ne__(self, other):
    return self.data <> other.data if other else False

  def __hash__(self):
    return hash(self.__data)

  def __repr__(self):
    return self.__data._name.encode('utf-8')

  def add_input_edge(self, edge):
    if edge.is_valid() and edge.endVertex == self:
      self.__inEdge.append(edge)
      self.__allEdge.append(edge)

  def add_output_edge(self, edge):
    if edge.is_valid() and edge.beginVertex == self:
      self.__outEdge.append(edge)
      self.__allEdge.append(edge)

  def add_edge(self, edge):
    self.__allEdge.append(edge)
    if edge.beginVertex == self:
      self.__outEdge.append(edge)
    else:
      self.__inEdge.append(edge)

  def remove_edge(self, edge):
    if edge in self.edges:
      self.__allEdge.remove(edge)
      if edge in self.inEdge:
        self.__inEdge.remove(edge)
      else:
        self.__outEdge.remove(edge)

  def __getitem__(self, index):
    return self.__allEdge[index]

  def edge_count(self):
    return len(self.__inEdge)

  @property
  def edges(self):
    return self.__allEdge

  @property
  def inEdge(self):
    return self.__inEdge

  @property
  def outEdge(self):
    return self.__outEdge

  @property
  def data(self):
    return self.__data


class Edge(object):
  def __init__(self, start=None, end=None, length=0):
    self.__beginVertex = start
    self.__endVertex = end
    self.__len = length
    self.__isValid = True
    self.__beginVertex.add_output_edge(self)
    self.__endVertex.add_input_edge(self)

  @property
  def isValid(self):
    return self.__isValid

  @isValid.setter
  def isValid(self, val):
    self.__isValid = val

  @property
  def endVertex(self):
    return self.__endVertex

  @endVertex.setter
  def endVertex(self, vertex):
    self.__endVertex = vertex

  @property
  def beginVertex(self):
    return self.__beginVertex

  @beginVertex.setter
  def beginVertex(self, vertex):
    self.__beginVertex = vertex

  @property
  def length(self):
    return self.__len

  @length.setter
  def length(self, length):
    self.__len = length

  def is_valid(self):
    return self.beginVertex and self.endVertex and self.__isValid

  def __eq__(self, other):
    return (self.__beginVertex, self.__endVertex, self.__len) == (
      other.__beginVertex, other.__endVertex, other.__len)

  def __hash__(self):
    return hash(
      (self.__len, self.__beginVertex.data._name, self.__endVertex.data._name))

  def __repr__(self):
    return self.beginVertex.data._name.encode('utf-8') + \
           ' ---' + str(self.__len) + '---> ' + \
           self.endVertex.data._name.encode('utf-8')


