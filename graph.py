#-*- coding: utf-8 -*-


class Graph(object):
  """
  Описывает сущность Граф. Определяет представление задач на карте.
  """
  def __init__(self, vertexes=None, edges=None):
    if not vertexes: vertexes = []
    if not edges: edges = []
    self._vertex = vertexes
    self._edge = edges
    if self._edge:
      self.remove_imaginary_edge()

  def remove_imaginary_edge(self):
    """
    Удаляет ребра между недостижимыми вершинами
    """
    for fromVertex in self._vertex:
      for toVertex in self._vertex:
        edge = self.get_edge(fromVertex, toVertex)
        if not fromVertex == toVertex and edge:
          time = fromVertex.data._startArrive + fromVertex.data._taskTime + edge.length
          if time > toVertex.data._endArrive:
            self._edge.remove(edge)

  def add_vertex(self, vertex):
    """
    Добавляет вершину в граф, связывая ее с другими вершинами
    @param vertex Добавляемая вершина
    """
    self._vertex.append(vertex)
    for edge in vertex.edges:
      if not ({edge.beginVertex, edge.endVertex} - set(self._vertex)):
        self._edge.append(edge)
    self._edge = list(set(self._edge))

  def add_edge(self, edge):
    """
    Добавляет ребро в граф
    """
    if edge.is_valid():
      self._edge.append(edge)

  def remove_vertex(self, vertex):
    """
    Удаляет вершину из графа, удаляя так же и ребра, имеющие отношения в ней
    @param vertex Удаляемая вершина
    """
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
    """
    Удаляет ребро из графа. У вершина оно остается.
    @param edge Удаляемое ребро
    """
    if edge in self._edge:
      self._edge.remove(edge)

  def remove_edge(self, index):
    """
    Удаляет ребро из графа. У вершина оно остается.
    @param index Индекс удаляемого ребра в списке
    """
    if index < len(self._edge):
      self._edge.remove(self._edge[index])

  def get_vertex(self, index):
    """
    Получает вершину графа по индексу в списке вершин
    @param index Индекс вершины в списке
    @return Врешина графа
    """
    if index < self.get_vertex_count():
      return self._vertex[index]
    else:
      return self._vertex[-1]

  def get_edge(self, begin, end):
    """
    Получает ребро графа по его концу и началу.
    @param begin Начало ребра
    @param end Конец ребра
    @return Ребро графа или None если такого нет
    """
    if not begin == end and not ({begin, end} - set(self._vertex)):
      for edge in begin.outEdge:
        if edge.endVertex == end:
          return edge
    return None

  def get_vertex_count(self):
    """
    @return Количество вершин в графе
    """
    return len(self._vertex)

  def get_edge_count(self):
    """
    @return Количество ребер в графе
    """
    return len(self._edge)

  def __iter__(self):
    for vertex in self._vertex:
      yield vertex


class Vertex(object):
  """
  Описывает сущность Вершина графа
  """
  def __init__(self, data=None, outEdges=None, inEdges=None):
    if not outEdges: outEdges = []
    if not inEdges: inEdges = []
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

  def add_edge(self, edge):
    """
    Добавляет ребро, принадлежащее вершине
    @param edge Добавляемое ребро
    """
    self.__allEdge.append(edge)
    if edge.beginVertex == self:
      self.__outEdge.append(edge)
    else:
      self.__inEdge.append(edge)

  def remove_edge(self, edge):
    """
    Удаляет ребро, принадлежащее вершине
    @param edge Удаляемое ребро
    """
    if edge in self.edges:
      self.__allEdge.remove(edge)
      if edge in self.inEdge:
        self.__inEdge.remove(edge)
      else:
        self.__outEdge.remove(edge)

  def __getitem__(self, index):
    return self.__allEdge[index]

  def get_out_edge(self, vertex):
    """
    @return ребро, концом которого явлется vertex
    """
    for edge in self.outEdge:
      if edge.endVertex == vertex:
        return edge
    return None

  def get_in_edge(self, vertex):
    """
    @return ребро, началом которого явлется vertex
    """
    for edge in self.inEdge:
      if edge.beginVertex == vertex:
        return edge
    return None

  def edge_count(self):
    """
    @return количество ребер, принадлежащих вершине 
    """
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
  """
  Описывает сущность Ребро в графе. Необходим для соединения вершин.
  """
  def __init__(self, start=None, end=None, length=0):
    self.__beginVertex = start
    self.__endVertex = end
    self.__len = length
    self.__isValid = True
    self.__beginVertex.add_edge(self)
    self.__endVertex.add_edge(self)

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


