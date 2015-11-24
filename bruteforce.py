# -*- coding: utf-8 -*-
__author__ = 'E.Vasilyev'
import copy
import itertools
import operator
import time
from Entity import *

# def Foo(вершины, пути):
#   добавить в пути вершины
#   говорим, что эти вершины теперь посещены
#   положим в очереди все необслуженные вершины, в  которе можно попасть
#   т.е. на кажду вершины своя очередь
#
#   осуществить полный перебор вершин из очередей
#   если очереди пусты, значит добавим пути в список вариантов
#   скопировать текущий путь и передать в Foo
#   для каждого варианта из полного перебора вызывать Foo(новые вершины)


allPath = []


def getTime(path, graph):
  base = None
  for v in graph._vertex:
    if v.data._isBase:
      base = v
  if path[0].data._startArrive > 8 + graph.get_edge(base, path[0]).length:
    time = path[0].data._taskTime + path[0].data._startArrive
  else:
    time = 8+graph.get_edge(base, path[0]).length + path[0].data._taskTime
  for i, vertex in enumerate(path):
    if i < len(path) - 1:
      edgeLen = graph.get_edge(vertex, path[i+1]).length
      if time + edgeLen < path[i+1].data._endArrive:
        if time + edgeLen < path[i+1].data._startArrive:
          time = path[i+1].data._startArrive + path[i+1].data._taskTime
        else:
          time += path[i+1].data._taskTime + edgeLen

  return time



def findNext(vertex, visited, path, workers, graph):
  """
  Проверить список исходящих ребер. Для каждой вершины своя очередь.
  Занести в очереди следующие вершины.
  """
  nextVertex = []
  for v, w, p in zip(vertex, workers, path):
    validVertex = [v]
    if not v.data._isBase:
      validVertex = []
      for e in v.outEdge:
        edge = graph.get_edge(v, e.endVertex)
        if e.endVertex.isValid and not e.endVertex in visited \
           and w.is_valid_client(e.endVertex) and edge:
          time = getTime(p, graph) + edge.length
          if time < e.endVertex.data._endArrive:
            validVertex.append(e.endVertex)
    nextVertex.append(validVertex)

  return nextVertex

def doPath(vertex, path, visited, workers, graph):
  """ осуществляет поиск в ширину  """

  for v, p in zip(vertex, path):
    if v.data._name <> 'base':
      p.append(v)
      visited.append(v)

  nextVertex = findNext(vertex, visited, path, workers, graph)
  #Выбрать выриант множества вершин из списков следующих вершин
  for newVertex in list(itertools.product(*nextVertex)):
    nV = list(copy.deepcopy(newVertex))
    v = list(set(nV))
    for i in reversed(xrange(len(nV))):
      if nV[i].data._name == 'base':
        nV.remove(nV[i])
    for x in v:
      if x.data._name == 'base':
        v.remove(x)
    if len(set(newVertex)) > 1 and len(nV) == len(v):
    # Запускаем рекурсию
      doPath(newVertex, copy.deepcopy(path), copy.deepcopy(visited), workers, graph)
  if len(allPath) % 100 == 0:
    print 'Количество путей: {0}'.format(len(allPath))
  allPath.append(path)

def cretePath(graph, workers):
  t1 = time.time()
  workerValidVertex = []
  for w in workers:
    validVertex = []
    for v in graph._vertex:
      if w.is_valid_client(v):
        validVertex.append(v)
    workerValidVertex.append(validVertex)
  j = 0
  # Полный перебор всех возможных вариантов начальных расстановок
  for comb in list(itertools.product(*workerValidVertex)):
    j += 1
    nV = list(copy.deepcopy(comb))
    v = list(set(nV))
    for i in reversed(xrange(len(nV))):
      if nV[i].data._name == 'base':
        nV.remove(nV[i])
    for x in v:
      if x.data._name == 'base':
        v.remove(x)
    if len(set(comb)) > 1 and len(nV) == len(v):
      doPath(list(comb), [list() for _ in xrange(len(comb))], [], workers, graph)

  print 'Без учета условий: {0}'.format(j)
  t2 = time.time()
  print 'Время: {0}'.format(t2-t1)
  return allPath

def bruteforce(graph, workers):
  print 'Поехали!'
  result = cretePath(graph, workers)
  print len(result)
  for v in graph._vertex:
    if v.data._isBase:
      base = v

  rank = {}

  for path in result:
    route = {}
    for concretePath, worker in zip(path, workers):
      concretePath.insert(0, base)
      p = Path(base, vertexes=concretePath)
      p.remove_useless_edge()
      route[worker] = p
    individ = Individual(route)
    rank[individ] = individ.get_cost()
#    print path, rank[individ]
  best = sorted(rank.iteritems(), key=operator.itemgetter(1), reverse=True)[0]
#  for i in sorted(rank.iteritems(), key=operator.itemgetter(1)):
#    print i[1]
  return best