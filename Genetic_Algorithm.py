# -*- coding: utf-8 -*-
import random
import time
import copy
import operator
from Entity import Population


def get_unvisit_client(specimen, graph):
  allVertex = []
  for path in specimen:
    allVertex.extend(path._vertex)
  return list(set(graph._vertex) - set(allVertex))


class GeneticAlgorithm(object):
  def __init__(self, max_generation=1, population_size=10, mutation=0.2,
               elite=0.1):
    self.__mutagen = mutation
    self.__elite = elite
    self.__maxGeneration = max_generation
    self._population = Population(population_size)
    self._newGeneration = Population(population_size)

  def create_population(self, workers, graph):
    self._population.create_area(workers, graph)

  def mutation(self, graph):
    specimens = random.sample(self._newGeneration.flock.keys(), int(round(self._newGeneration.get_count() * self.__mutagen)))
    for specimen in specimens:
      operator = self.__selectMutateOperator(random.random())
      newSpecimen = operator(specimen, graph)
      if not newSpecimen.is_valid():
        print newSpecimen
      del(self._newGeneration.flock[specimen])
      self._newGeneration.add_spiec(newSpecimen)

  def __replacement(self, specimen, *args):
    """
    Заменяет в одном из путей клиента на одного из необслуженных
    @param specimen Обход графа, который необходимо мутировать
    @param graph исходный граф
    @return Нового члена общества
    """
    t1 = time.time()
    unVisit = get_unvisit_client(specimen, args[0])
    if unVisit:
      newSpecimen = copy.deepcopy(specimen)
      random.shuffle(unVisit)
      for replVertex in unVisit:
        temp = newSpecimen.route.keys()
        random.shuffle(temp)
        for worker in temp:
          if worker.is_valid_client(replVertex):
            changePath = newSpecimen.route[worker]
            flag = False
            if changePath.get_len():
              for i in xrange(1, len(changePath._vertex) - 1):
                delVertex = changePath._vertex[i]
                changePath.remove_vertex(delVertex)
                changePath.insert_vertex(i, replVertex)
                if newSpecimen.is_valid():
                  flag = True
                  break
                newSpecimen.route[worker] = copy.deepcopy(specimen.route[worker])
                changePath = newSpecimen.route[worker]
            else:

              changePath.insert_vertex(1, replVertex)
              flag = True
            if flag:
              t2 = time.time()
              print 'Mutation(replacement): {0}'.format(t2-t1)
              return newSpecimen
    return specimen

  def __delete(self, specimen, *args):
    t1 = time.time()
    stop = 0
    while stop < 30 and specimen.get_client_count():
      experimental = copy.deepcopy(specimen)
      path = random.choice(experimental.route.values())
      if path.get_len():
        vertex = random.choice(path._vertex[1:-1])
        path.remove_vertex(vertex)
        t2 = time.time()
        print 'Mutation(delete): {0}'.format(t2-t1)
        return experimental
      stop += 1
    return specimen

  def __insert(self, specimen, *args):
    """
    Мутация путем вставки в путь необслуженного клиента
    @param specimen Обход графа, который необходимо мутировать
    @param args Необходим для совмещения с другими функциями мутации
    @return Нового члена общества
    """
    t1 = time.time()
    unVisit = get_unvisit_client(specimen, args[0])
    if unVisit:
      random.shuffle(unVisit)
      for insVertex in unVisit:
        clone = copy.deepcopy(specimen)
        workers = clone.route.keys()
        random.shuffle(workers)
        for worker in workers:
          if worker.is_valid_client(insVertex):
            etalonPath = specimen.route[worker]
            for index in xrange(1, etalonPath.get_len()+2):
              insPath = clone.route[worker]
              insPath.insert_vertex(index, insVertex)
              if clone.is_valid():
                t2 = time.time()
                print 'Mutation(insert): {0}'.format(t2-t1)
                return clone
              clone = copy.deepcopy(specimen)
    return specimen

  def __swapIn(self, specimen, *args):
    """
    Мутация путем обмена клиентов между путями монтеров
    @param specimen Обход графа, который необходимо мутировать
    @param args Необходим для совмещения с другими функциями мутации
    @return Нового члена общества
    """
    t1 = time.time()
    stop = 0
    while True and specimen.get_client_count() and stop < 30:
      mutateVertex = {}
      choiceRoute = copy.deepcopy(specimen.route)
      for i in xrange(2):
        worker = random.choice(choiceRoute.keys())
        if choiceRoute[worker].get_len():
          choiceVertex = random.choice(choiceRoute[worker]._vertex[1:-1])
          del(choiceRoute[worker])
          mutateVertex[worker] = choiceVertex
        else:
          mutateVertex[worker] = None
      flag = True
      if len(list(set(mutateVertex.values()))) > 1:
        for k in mutateVertex:
          for v in mutateVertex.values():
            if v and not k.is_valid_client(v):
              flag = False
        
        if flag:
          experimental = copy.deepcopy(specimen)
          experimental.swap(mutateVertex.values())
          if experimental.is_valid():
            t2 = time.time()
            print 'Mutation(swap): {0}'.format(t2-t1)
            return experimental
      stop += 1
    return specimen


  def __shuffle(self, specimen, *args):
    t1 = time.time()
    clone = copy.deepcopy(specimen)
    allPath = [p for p in clone.route.values() if p.get_len() > 1]
    if allPath:
      random.shuffle(allPath)
      for path in allPath:
        etalon = copy.deepcopy(path)
        vertex = path._vertex[1:-1]
        stop = 0
        while stop < 10:
          stop += 1
          random.shuffle(vertex)
          path._vertex[1:-1] = vertex
          path.remove_useless_edge()
          if clone.is_valid():
            t2 = time.time()
            print 'Shuffle: {0}'.format(t2 - t1)
            return clone
          path = etalon

    return specimen

  def __selectMutateOperator(self, chance):
    if chance < 0.1:
      operator = self.__delete
    elif chance < 0.25:
      operator = self.__replacement
    elif chance < 0.4:
      operator = self.__insert
    elif chance < 0.7:
      operator = self.__shuffle
    else:
      operator = self.__swapIn
    return operator

  def crossover(self, parents):
    """
    BCRC оператор скрещивания
    @param parents Список с родителями
    @return список новых потомка
    """
    childCnt = len(parents)/2
    offspring = []
    for i in xrange(childCnt):
      childs = copy.deepcopy(random.sample(parents, 2))
      if random.random() > 0.85:
        parents = list(set(parents) - set(childs))
        replacePath = [copy.deepcopy(random.choice(childs[0].route.values())),
                       copy.deepcopy(random.choice(childs[1].route.values()))]

        for i,j in zip(replacePath[0]._vertex[1:-1], replacePath[1]._vertex[1:-1]):
          childs[1].remove_vertex(i)
          childs[0].remove_vertex(j)
        replaceVertex = replacePath[0]._vertex[1:-1] + replacePath[1]._vertex[1:-1]
        for vertex in replaceVertex:
          for individ in childs:
            if not individ.has_vertex(vertex):
              individ.insert_vertex(vertex)
      offspring.extend(childs)
    return offspring

  def selection(self):
    for spec in sorted(self._population.flock.iteritems(), key=operator.itemgetter(1),reverse=True):
      if self._newGeneration.get_count() >= self._newGeneration._size:
        break
      self._newGeneration.add_spiec(spec[0])

    self._population = copy.deepcopy(self._newGeneration)
    self._newGeneration.clear()

  def run(self, workers, graph):
    t1 = time.time()
    self.create_population(workers, graph)
    t2 = time.time()
    print 'Create population: {0}'.format(t2 - t1)
    for j in xrange(self.__maxGeneration):
      print 'Поколение: {0}'.format(j)
      parents = self._population.get_parents()
      t3 = time.time()
      childs = self.crossover(parents)
      t4 = time.time()
      print 'Crossover: {0}'.format(t4 - t3)
      for child in childs:
        self._newGeneration.add_spiec(child)
      print self._newGeneration.get_count()
      self.mutation(graph)
      self.selection()
      best = sorted(self._population.flock.iteritems(), key=operator.itemgetter(1))[-1]
      print 'Лучший: ' + str(best[1])
      print 'Худший: ' + str(sorted(self._population.flock.iteritems(), key=operator.itemgetter(1))[0][1])
      print [x._vertex for x in best[0].route.values()]
      print '=========================='

    return sorted(self._population.flock.iteritems(), key=operator.itemgetter(1))[-1]

