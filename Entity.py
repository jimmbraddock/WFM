# -*- coding: utf-8 -*-
import copy
import random
import operator
from graph import Graph


TOURNAMENT_RATE = 3
NORMAL_TIME_WORK = 8

class Task(object):
  """
  Описывает данные, которые отображает вершина графа
  """
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
    self._address = props[11]

  def __eq__(self, other):
    return (self._name, self._taskType, self._prior) == (other._name, other._taskType, other._prior)

  def __ne__(self, other):
    return (self._name, self._taskType, self._prior) <> (other._name, other._taskType, other._prior)

  def __hash__(self):
    return hash((self._name, ';'.join(self._taskType), self._prior))

  def __repr__(self):
    return 'Клиент: {0}'.format(self._name)


class Worker(object):
  """
  Описывает сущность Монтер
  """
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
    base = None
    for vertex in graph:
      if vertex.data._isBase:
        base, node = vertex, vertex
        break
    path = Path(base)
    time = 8
    # TODO: понять почему вершины могут попасть в маршруты разных монтеров. Дублирование вершин.

    if random.random() > 0.1:
      pretender = [x.endVertex for x in graph._edge if x.endVertex.isValid and base == x.beginVertex]
      if pretender:
        node = random.choice(pretender)
        time += base.get_out_edge(node).length
        if time < node.data._startArrive:
          time = node.data._startArrive
      else:
        node = path.start
    while True:
      path.add_vertex(copy.deepcopy(node))
      if path.start == node:
        break
      node.isValid = False
      stop = 0
      while stop < 30 and node.outEdge:
        choice = [x.endVertex for x in graph._edge if x.endVertex.isValid
                                        and node == x.beginVertex
                                        and x.endVertex.data._endArrive > time]
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
    """
    Проверяет валидность клиента по навыку
    @param vertex Исследуемая вершина
    @return True или False
    """
    return not (set(list(vertex.data._taskType)) - set(list(self.__skill)))

  @property
  def name(self):
    return self.__name

  @property
  def skill(self):
    return self.__skill

  def __hash__(self):
    return hash((self.__name, ';'.join(self.__skill)))

  def __eq__(self, other):
    return (self.__name, self.__skill) == (other.name, other.skill)


class Path(Graph):
  """
  Описывает путь монтера. Является наследником от графа
  """
  def __init__(self, start, vertexes=None, edges=None):
    super(Path, self).__init__(vertexes, edges)
    self.start = start
    self.add_vertex(self.start)

  def remove_useless_edge(self):
    """
    Удаляет ненужные ребра, чтобы путь был строго однонаправленным
    """
    newEdges = []
    if self.get_len():
      for ind, vertex in enumerate(self._vertex):
        if ind < len(self._vertex) - 1:
          edge = self.get_edge(vertex, self._vertex[ind+1])
          if edge:
            newEdges.append(edge)
    self._edge = newEdges

  def get_len(self):
    return len(self._vertex) - 2

  def is_valid(self, worker):
    """
    Проверяет корректность пути для монтера по навыку и временному окну
    @param worker Монтер, для которого осуществляется проверка
    @return True или False
    """
    if self.start.data == self._vertex[-1].data and\
       (self.get_edge_count() == self.get_len() + 1 or not self.get_len()):

      time = 8
      if self.get_len():
        for i, v in enumerate(self._vertex):
          if i < len(self._vertex) - 1:
            nextV = self._vertex[i+1]
            time += v.data._taskTime + v.get_out_edge(nextV).length
            if time < nextV.data._endArrive and worker.is_valid_client(nextV):
              if time < nextV.data._startArrive:
                time = nextV.data._startArrive
            else:
              return False

          # if time + j.length < i.data._endArrive and worker.is_valid_client(i):
          #   if time + j.length < i.data._startArrive:
          #     time = i.data._startArrive + i.data._taskTime
          #   else:
          #     time += j.length + i.data._taskTime
          # else:
          #   return False
      return True
    return False

  def insert_vertex(self, index, vertex):
    """
    Вставка вершины в путь
    @param index индекс в списке, куда вставить вершину
    @param vertex вставляемая вершина
    """
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
    return ('---'.join([v.data._name for v in self._vertex])).encode('utf-8')


class Individual(object):
  """
  Описывает индивида в генетичеком алгоритме. Представляет вариант обхода графа
  """
  def __init__(self, route=None):
    if not route: route = {}
    self.__route = route

  def swap(self, swapVertex):
    """
    Производит обмен вершинами между путями монтеров
    @param swapVertex Список вершин, подлежащих обмену. Вид [v1, v2]
    """
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
    """
    Оценочная функция. Определяет степень пригодности варианта обхода графа
    @return Оценка обхода
    """
    total = []
    for path in self.__route.values():
      prior = []
      vertexServed = 0
      timeRoad, timeWork = 0, 0
      fitWorker = 0
      if path.get_len():
        vertexServed = path.get_len()  # Не учитываем базу
        for vertex in path:
          prior.append(vertex.data._prior)
          timeWork += vertex.data._taskTime
        for edge in path._edge:
          timeRoad += edge.length
        fitWorker = vertexServed*timeWork*sum(prior)/len(prior)/timeRoad
      total.append(fitWorker)
    return sum(total)/len(total) if total else 0

  def remove_vertex(self, vertex):
    """
    Удаление вершины из обхода
    @param vertex Исключаемая из обхода вершина
    """
    for path in self.__route.values():
      if vertex in path._vertex:
        path.remove_vertex(vertex)

  def has_vertex(self, vertex):
    """
    Проверяет вхождение вершины в путь
    @param vertex Проверяемая вершина
    @return Входит или не входит вершина в обход графа
    """
    for path in self.__route.values():
      if vertex in path._vertex:
        return True
    return False

  def insert_vertex(self, vertex):
    """
    Вставляет вершину в один из путей на основании оценочной функции
    @param vertex Вставляемая вершина
    """
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
      bestIns = sorted(variants.keys(), reverse=True)[0]
      self.__route[variants[bestIns][1]].insert_vertex(variants[bestIns][0], vertex)

  def filling(self, workers, graph):
    """
    Составляет обход графа монтерами
    @param workers Список монтеров, участвующих в обходе
    @param graph Исследуемый граф
    """
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
    flag = True
    allVertex = [v for x in self.__route.values() for v in x._vertex[1:-1]]
    if len(set(allVertex)) <> len(allVertex):
      flag = False
    if flag:
      for worker, path in self.__route.iteritems():
        if not path.is_valid(worker):
          flag = False
    return flag

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
  def __init__(self, size, flock=None, crossover_rate=0.8):
    if not flock: flock = {}
    self.__flock = flock
    self._size = size
    self._crossover_rate = crossover_rate

  def get_parents(self):
    """
    Выбираются пары родителей для скрещивания турнирным методом
    """
    parents = []
    pickParent = self.__flock.keys()
    select = int(round(self._crossover_rate*len(self.__flock)))
    parentCnt = select - 1 if select % 2 else select
    while parentCnt:
      assumeParent = sorted(random.sample(pickParent, TOURNAMENT_RATE),
                            key=Individual.get_cost, reverse=True)
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
    while self._size > len(self.__flock) and stop < self._size * 3:
      individ = Individual()
      individ.filling(workers, copy.deepcopy(graph))
      self.__flock[individ] = individ.get_cost()
      stop += 1
    print 'Population size: {0}'.format(len(self.__flock))

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
