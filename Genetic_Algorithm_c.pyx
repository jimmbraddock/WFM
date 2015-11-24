# -*- coding: utf-8 -*-
import random
import copy
import operator
from Entity_c import Population


MAX_GENERATION = 1

def get_unvisit_client(specimen, graph):
  allVertex = []
  for path in specimen:
    allVertex.extend(path._vertex)
  return list(set(graph._vertex) - set(allVertex))


class GeneticAlgorithm(object):
  def __init__(self, mutation=0.2, elite=0.1):
    self.__mutagen = mutation
    self.__elite = elite
    self._population = Population()
    self._newGeneration = Population()

  def create_population(self, workers, graph):
    self._population.create_area(workers, graph)

  def mutation(self, graph):
    specimens = random.sample(self._newGeneration.flock.keys(), int(self._newGeneration.get_count() * self.__mutagen))
    mutateType = [self.__swapIn, self.__delete, self.__insert, self.__replacement]
    for specimen in specimens:
      newSpecimen = random.choice(mutateType)(specimen, graph)
      del(self._newGeneration.flock[specimen])
      self._newGeneration.add_spiec(newSpecimen)
    self._newGeneration.add_spiec(copy.deepcopy(sorted(self._population.flock.iteritems(), key=operator.itemgetter(1))[-1][0]))
    for k in self._newGeneration:
      self._population.add_spiec(k)

  def __replacement(self, specimen, *args):
    """
    Заменяет в одном из путей клиента на одного из необслуженных
    @param specimen Обход графа, который необходимо мутировать
    @param graph исходный граф
    @return Нового члена общества
    """
    unVisit = get_unvisit_client(specimen, args[0])
    stop = 0
    while stop < 30 and unVisit:
      subject = copy.deepcopy(specimen)
      replVertex = random.choice(unVisit)
      changePath = random.choice(subject.route.values())
      if changePath.get_len():
        delVertex = random.choice(changePath._vertex[1:-1])
        index = changePath._vertex.index(delVertex)
        changePath.remove_vertex(delVertex)
        changePath.insert_vertex(index, replVertex)
      else:
        changePath.insert_vertex(1, replVertex)
      if subject.is_valid():
        return subject
      stop += 1
    return specimen

  def __delete(self, specimen, *args):
    stop = 0
    while stop < 30 and specimen.get_client_count():
      experimental = copy.deepcopy(specimen)
      path = random.choice(experimental.route.values())
      if path.get_len():
        vertex = random.choice(path._vertex[1:-1])
        path.remove_vertex(vertex)
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
    unVisit = get_unvisit_client(specimen, args[0])
    stop = 0
    while stop < 30 and unVisit:
      subject = copy.deepcopy(specimen)
      insPath = random.choice(subject.route.values())
      insVertex = random.choice(unVisit)
      index = random.choice([x for x in xrange(1, insPath.get_len() + 1)]) if insPath.get_len() else 1
      insPath.insert_vertex(index, insVertex)
      if subject.is_valid():
        return subject
      stop += 1
    return specimen

  def __swapIn(self, specimen, *args):
    """
    Мутация путем обмена клиентов между путями монтеров
    @param specimen Обход графа, который необходимо мутировать
    @param args Необходим для совмещения с другими функциями мутации
    @return Нового члена общества
    """
    stop = 0
    while True and specimen.get_client_count():
      mutateVertex = []
      if stop > 30:
        break
      choiceRoute = copy.deepcopy(specimen.route.values())
      for i in xrange(2):
        path = random.choice(choiceRoute)
        if path.get_len():
          choiceVertex = random.choice(path._vertex[1:-1])
          choiceRoute.remove(path)
          mutateVertex.append(choiceVertex)
        else:
          mutateVertex.append(None)
      if len(list(set(mutateVertex))) > 1:
        experimental = copy.deepcopy(specimen)
        experimental.swap(mutateVertex)
        if experimental.is_valid():
          return experimental
      stop += 1
    return specimen

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
    delSpecimen = [x[0] for x in sorted(self._population.flock.items(), key=lambda x: x[1])][:-self._population._size]
    for specimen in delSpecimen:
      del(self._population.flock[specimen])

  def run(self, workers, graph):
    #print 'start algorithm'
    self.create_population(workers, graph)
    #print 'END create population'
    for j in xrange(MAX_GENERATION):
      #print 'Generation: ' + str(j)
      parents = self._population.get_parents()
      childs = self.crossover(parents)
      #print 'End crossover'
      for child in childs:
        self._newGeneration.add_spiec(child)
      #print 'Start Mutation'
      self.mutation(graph)
      #print 'end mutation'
      self.selection()
      #print 'end selection'
      #print '=========================='

    return sorted(self._population.flock.iteritems(), key=operator.itemgetter(1))[-1]

