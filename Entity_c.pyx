# -*- coding: utf-8 -*-
import copy
import random
from graph_c import Graph


TOURNAMENT_RATE = 3
NORMAL_TIME_WORK = 8

class Task(object):
  def __init__(self, props):
    self._name = props[0]
    self._prior = props[1]
    self._startArrive = props[2]
    self._endArrive = props[3]
    self._taskTime = props[4]
    self._taskType = props[5]
    self._wasVisited = False
    self._isBase = props[6]
    self._longitude = props[7]
    self._latitude = props[8]
    self._taskNumber = props[9]
    self._clientId = props[10]

  def __eq__(self, other):
    return (self._name, self._taskType, self._prior) == (other._name, other._taskType, other._prior)

  def __ne__(self, other):
    return (self._name, self._taskType, self._prior) <> (other._name, other._taskType, other._prior)

  def __hash__(self):
    return hash((self._name, self._taskType, self._prior))

  def __repr__(self):
    return 'Клиент: {0}'.format(self._name)


class Worker(object):
  def __init__(self, name, skill):
    self.__skill = skill
    self.__name = name.encode('utf-8')

  def find_path(self, graph):
    """
    Поиск варианта обхода графа для монтера
    @param graph Граф обхода, в котором уже удалены клиенты с неподходящим типом задачи
    @return Путь монтера в графе
    """
    node = None
    for vertex in graph:
      if vertex.data._isBase:
        node = vertex
        break
    path = Path(node)
    time = node.data._startArrive + node.data._taskTime
    # TODO: очень проблемная зона, вылетает часто из-за пустоого списка при рандоме
    if random.random() > 0.1:
      if node.outEdge:
        node = (random.choice(
          [x.endVertex for x in graph._edge if x.endVertex.isValid and node == x.beginVertex]))
      else:
        node = path.start
    while True:
      path.add_vertex(copy.deepcopy(node))
      if path.start == node:
        break
      node.isValid = False
      stop = 0
      while stop < 30 and node.outEdge:
        choice = [x.endVertex for x in graph._edge if x.endVertex.isValid and node == x.beginVertex]
        nextNode = random.choice(choice)
        edgeLen = graph.get_edge(node, nextNode).length
        if time + node.data._taskTime + edgeLen < nextNode.data._endArrive:
          if time + node.data._taskTime + edgeLen < nextNode.data._startArrive:
            time = nextNode.data._startArrive
          else:
            time += node.data._taskTime + edgeLen
          graph.remove_vertex(node)
          node = nextNode
          break
        stop += 1
    path.remove_useless_edge()
    return path

  def is_valid_client(self, vertex):
    return not (set(list(vertex.data._taskType)) - set(list(self.__skill)))

  @property
  def name(self):
    return self.__name

  @property
  def skill(self):
    return self.__skill

  def __hash__(self):
    return hash((self.__name, self.__skill))

  def __eq__(self, other):
    return (self.__name, self.__skill) == (other.name, other.skill)


class Path(Graph):
  def __init__(self, start, vertexes=None, edges=None):
    super(Path, self).__init__(vertexes, edges)
    self.start = start
    self.add_vertex(copy.deepcopy(self.start))

  def remove_useless_edge(self):
    newEdges = []
    for ind, vertex in enumerate(self._vertex):
      if ind < len(self._vertex) - 1:
        newEdges.append(self.get_edge(vertex, self._vertex[ind+1]))
    self._edge = newEdges

  def get_len(self):
    return len(self._vertex) - 2

  def is_valid(self, worker):
    if self.start.data == self._vertex[-1].data and\
       (self.get_edge_count() == self.get_len() + 1 or not self.get_len()):
      time = self.start.data._startArrive
      if self.get_len():
        for i, j in zip(self._vertex[1:], self._edge):
          if time + j.length < i.data._endArrive and worker.is_valid_client(i):
            if time + j.length < i.data._startArrive:
              time += i.data._startArrive + i.data._taskTime
            else:
              time += j.length + i.data._taskTime
          else:
            return False
      return True
    return False

  def insert_vertex(self, index, vertex):
    delEdge = self.get_edge(self._vertex[index - 1], self._vertex[index])
    if delEdge and delEdge in self._edge:
      self._edge.remove(delEdge)
    for edge in vertex.edges:
      if self._vertex[index - 1] == edge.beginVertex or\
         self._vertex[index] == edge.endVertex:
        self._edge.append(edge)
    self._vertex.insert(index, vertex)

  def __eq__(self, other):
    result = False
    if self.get_len() == other.get_len():
      result = True
      for i, j in zip(self._vertex, other._vertex):
        if not i == j:
          result = False
          break
    return result

  def __hash__(self):
    return hash(tuple(self._vertex))

  def __repr__(self):
    return '---'.join([v.data._name for v in self._vertex])


class Individual(object):
  def __init__(self, route=None):
    if not route: route = {}
    self.__route = route

  def swap(self, swapVertex):
    if None in swapVertex:
      vertex = swapVertex[0] if swapVertex[0] else swapVertex[1]
      for path in self.__route.values():
        if vertex in path:
          path.remove_vertex(vertex)
        elif not path.get_len():
          path.insert_vertex(1, vertex)
    else:
      for path in self.__route.values():
        if swapVertex[0] in path:
          index = path._vertex.index(swapVertex[0])
          path.remove_vertex(swapVertex[0])
          path.insert_vertex(index, swapVertex[1])
        elif swapVertex[1] in path:
          index = path._vertex.index(swapVertex[1])
          path.remove_vertex(swapVertex[1])
          path.insert_vertex(index, swapVertex[0])

  def get_cost(self):
    # TODO: необходимо переделать, попытаться учесть все зависимости или
    # разделить на несколько конкретных параметров минимизации
    """
    Оценочная функция. Определяет степень пригодности варианта обхода графа
    @return Оценка обхода
    """
    total, vertexCnt = 0.0, 0
    timeRoad, timeWork, prior = 0, 0, 0
    for path in self.__route.values():
      if path.get_len():
        vertexCnt += path.get_len()  # Не учитываем базу
        for vertex in path:
          prior += vertex.data._prior
          timeWork += vertex.data._taskTime
        for edge in path._edge:
          timeRoad += edge.length
        fitWorker = timeWork*prior*(NORMAL_TIME_WORK + timeRoad)/8*timeRoad
        total += fitWorker
    return total * vertexCnt

  def remove_vertex(self, vertex):
    for path in self.__route.values():
      if vertex in path._vertex:
        path.remove_vertex(vertex)

  def has_vertex(self, vertex):
    for path in self.__route.values():
      if vertex in path._vertex:
        return True
    return False

  def insert_vertex(self, vertex):
    variants = {}
    for worker, path in self.__route.items():
      for i in xrange(1, path.get_len()):
        etalonPath = copy.deepcopy(path)
        path.insert_vertex(i, vertex)
        if self.is_valid():
          variants[self.get_cost()] = (i, worker)
        path = etalonPath
        self.__route[worker] = etalonPath
    if variants.keys():
      bestIns = sorted(variants.keys())[0]
      self.__route[variants[bestIns][1]].insert_vertex(variants[bestIns][0], vertex)

  def filling(self, workers, graph):
    for worker in workers:
      specGraph = copy.deepcopy(graph)
      for vertex in specGraph:
        if not worker.is_valid_client(vertex):
          vertex.isValid = False
      #print 'start find path for worker %s' % worker.name
      self.__route[worker] = worker.find_path(specGraph)
      for delVertex in self.__route[worker]._vertex[1:-1]:
        graph.remove_vertex(delVertex)

  def get_client_count(self):
    return sum([path.get_len() for path in self.__route.values()])

  @property
  def route(self):
    return self.__route

  def is_valid(self):
    for worker, path in self.__route.iteritems():
      if not path.is_valid(worker):
        return False
    return True

  def __eq__(self, other):
    for i, j in zip(self.__route.values(), other.route.values()):
      if not i == j:
        return False
    return True

  def __hash__(self):
    return hash(tuple(self.__route.values()))

  def __repr__(self):
    return '///'.join([path.__repr__() for path in self.__route.values()])

  def __iter__(self):
    for path in self.__route.values():
      yield path


class Population(object):
  def __init__(self, flock=None, size=10, crossover_rate=0.8):
    if not flock: flock = {}
    self.__flock = flock
    self._size = size
    self._crossover_rate = crossover_rate

  def get_parents(self):
    """
    Выбираются пары родителей для скрещивания турнирным методом
    """
    pickParent = copy.deepcopy(self.__flock.keys())
    parents = []
    select = int(self._crossover_rate*len(self.__flock))
    parentCnt = select - 1 if select % 2 else select
    while parentCnt:
      assumeParent = random.sample(pickParent, TOURNAMENT_RATE)
      sorted(assumeParent)
      if random.random() < 0.5:
        parents.append(random.choice(assumeParent[1:]))
      else:
        parents.append(assumeParent[0])
      pickParent.remove(parents[-1])
      parentCnt -= 1
    return parents

  def clear(self):
    self.__flock = {}

  def add_spiec(self, spiec):
    self.__flock[spiec] = spiec.get_cost()

  def create_area(self, workers, graph):
    stop = 0
    #print 'start create area'
    while self._size <> len(self.__flock) and stop < self._size * 3:
      individ = Individual()
      individ.filling(workers, copy.deepcopy(graph))
      self.__flock[individ] = individ.get_cost()
      stop += 1
      print stop
    #print 'end create area'

  def get_count(self):
    return len(self.__flock)

  def remove_individ(self, individ):
    if individ in self.__flock:
      del(self.__flock[individ])

  @property
  def flock(self):
    return self.__flock

  def __iter__(self):
    for person in self.__flock.keys():
      yield person
