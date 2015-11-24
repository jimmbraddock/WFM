# -*- coding: utf-8 -*-
import sys
import MySQLdb as mdb
import time
import bruteforce
from random import randint
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import QWebView
from abc import ABCMeta, abstractmethod
from graph import Vertex, Edge, Graph
from Entity import Worker, Task
from Genetic_Algorithm import *


MAP = 'MapBypass.html'

class Observer(object):
  __metaclass__=ABCMeta

  @abstractmethod
  def update(self):
    pass

class Observable(object):
  def __init__(self):
    self._observers = []

  def addObserver(self, observer):
    self._observers.append(observer)

  def notifyUpdate(self):
    for observer in self._observers:
      observer.update()


class Model(Observable):
  def __init__(self):
    Observable.__init__(self)
    self.__graph = None
    self._observers = []
    bypass = self.getByPass()
    self.__individ = bypass
    self.getHtml()
    self.__timeline = ([x for x in xrange(8, 21)])

  def IsValid(self):
    for path in self.__individ.values():
      if not path.isValid():
        return False
    return True

  def getHtml(self):
    f = open(MAP, 'wb')
    allClients = [[c._longitude, c._latitude, c._startArrive,
                  c._endArrive, '<br/>'.join(c._taskType), c._taskTime, c._name]
                  for c in [vertex.data for vertex in self.__graph._vertex]]
    plannedClients = []
    workerName = []
    for worker in [w for w in self.__individ.route]:
      plannedClients.append([[v.data._latitude, v.data._longitude]
                             for v in self.__individ.route[worker]._vertex])
      workerName.append(worker.name.decode('utf-8'))

    allClients = str(allClients).replace('u\'', '\'').replace('L', '')
    workerName =  str(workerName).replace('u\'', '\'')
    callbacks, cbFunc, colors, htmlTable = self.__getHTMLattr()


    template = open('template.txt')
    data = template.read().format(workers=str(workerName),
                                  clients=str(allClients),
                                  servedClients=str(plannedClients),
                                  table=htmlTable,
                                  callbacks=callbacks,
                                  colors=colors,
                                  responseCb=cbFunc)
    f.write(data)
    f.close()
    template.close()

  def __getHTMLattr(self):
    callback = '['
    callbackBody = ''
    html = ''
    colors = ['#000000', '#6A5ACD', '#FF4500', '#228B22', '#4169E1', '#9932CC',
              '#FFFF00', '#FF00FF']
    for i, worker in enumerate(self.__individ.route):
      callback += '\'getRoute{0}\','.format(i)
      callbackBody += '''function getRoute{0}(response) {{getRouteCommon(response, lineLayer[{0}],colorPath[{0}]);}}\n'''.format(i)
      color = colors[i] if i < len(colors) else "#%x" % (randint(0, 16777215))
      colors.append(color)
      if self.__individ.route[worker].get_len():
        html += '''<tr>
                    <td>{0}</td>
                    <td bgcolor=\"{1}\"></td>
                </tr>'''.format(worker.name, color)
    callback = callback[:-1] + ']'
    return callback, callbackBody, str(colors), html

  def timeArrive(self, worker):
    time = [self.__individ.route[worker]._vertex[1].data._startArrive]
    taskTime = []
    for i, x in enumerate(self.__individ.route[worker]._vertex[1:-1]):
      if i < len(self.__individ.route[worker]._vertex[1:-1]) - 1:
        t = time[-1] + x.data._taskTime + \
            self.__individ.route[worker].get_edge(x, self.__individ.route[worker]._vertex[1:-1][i+1]).length
        time.append(t)
      taskTime.append(x.data._taskTime)

    return time, taskTime

  def changePath(self):
    self.notifyUpdate()

  def __requestFromDb(self):
    con = None
    try:
      con = mdb.connect(user='root', passwd='root', db='WFM', use_unicode=True,
                        charset='utf8')
      workers = self.__getWorker(con)
      vertex = self.__getVertex(con)
      edge = self.__getEdge(vertex, con)


    except mdb.Error, e:
      print "Error %d: %s" % (e.args[0],e.args[1])
      sys.exit(1)

    finally:
      if con:
        con.close()
    return vertex, edge, workers

  def __getWorker(self, con):
    worker = []
    cur = con.cursor()
    cur.execute('SET NAMES utf8')
    cur.execute('SET CHARACTER SET utf8')
    cur.execute('SET character_set_connection=utf8')
    cur.execute('SELECT name, skill from worker')
    rows = cur.fetchall()
    for row in rows:
      worker.append(Worker(row[0], row[1].split(';')))
    return worker

  def __getVertex(self, con):
    clients = []
    cur = con.cursor()
    cur.execute("SELECT c.name, t.priority, t.start_arrive, t.end_arrive, "
                "p.task_time, p.task_type, c.is_base, c.longitude, c.latitude,"
                " t.id,c.id, c.address FROM client c,task_type p, task t "
                "WHERE t.client_id=c.id and t.task_type_id=p.id "
                "or c.is_base=True group by c.id")
    rows = cur.fetchall()

    for row in rows:
      # Костыль для обработки точки выхода монтеров
      row = list(row)
      row[5] = row[5].split(';')
      if row[6]:
        row[1] = 0
        row[2] = 8
        row[3] = 20
        row[4] = 0
        row[5] = ''
        row[9] = 0
      clients.append(Vertex(data=Task(row)))
    return clients

  def __getEdge(self, vertexes, con):
    edge = []
    cur = con.cursor()
    for vertex in vertexes:
      for v in vertexes:
        if v <> vertex:
          query = "SELECT distance from distance d where d.CLIENT_FROM = %d and" \
                  " d.CLIENT_TO = %d" % (vertex.data._clientId, v.data._clientId)
          cur.execute(query)
          distance = cur.fetchone()[0]
          edge.append(Edge(vertex, v, distance))
    return edge

  def getByPass(self):
    start = time.time()
    vertex, edge, workers = self.__requestFromDb()
    self.__graph = Graph(vertex, edge)

    genetic = GeneticAlgorithm(max_generation=50, population_size=25)
    best = bruteforce.bruteforce(self.__graph, workers)
    #best = genetic.run(workers, self.__graph)
    print '==========================='
    finish = time.time()
    print (finish - start)
    for x in best[0].route.values():
      print x._vertex
      print x._edge
    return best[0]

  @property
  def individ(self):
    return self.__individ

  @property
  def graph(self):
    return self.__graph

  @property
  def timeline(self):
    return self.__timeline


class TimeRect(object):
  def __init__(self, x, y, w, h):
    self.x = x
    self.y = y
    self.width = w
    self.height = h

  def paint(self, qp):
    brush = QBrush(QColor(0, 255, 0))
    pen = QPen(QColor(0, 0, 0))
    qp.setPen(pen)
    qp.setBrush(brush)
    qp.drawRect(self.x, self.y, self.width, self.height)


class ClassMeta( pyqtWrapperType, ABCMeta ): pass


class View(QWidget, Observer):
  __metaclass__ = ClassMeta
  def __init__(self, controller, model, parent=None):
    QWidget.__init__(self, parent)
    self.setMinimumSize(500, 400)
    self.model = model
    self.model.addObserver(self)
    self.controller = controller

    self.graphic = Graphic(self.model, self)
    self.viewer = WebMap(self)
    self.taskTable = QTableWidget(self)
    self.workerTable = QTableWidget(self)
    self.fillLists()

    layout = QGridLayout(self)
    layout.setSpacing(10)
    layout.addWidget(self.graphic, 0, 0)
    layout.addWidget(self.viewer, 1, 0)
    layout.addWidget(self.taskTable, 1, 1)
    layout.addWidget(self.workerTable, 0, 1)

    self.setLayout(layout)

  def fillLists(self):
    workerRows = len(self.model.individ.route)
    workerCols = 2
    self.workerTable.setRowCount(workerRows)
    self.workerTable.setColumnCount(workerCols)
    self.workerTable.setHorizontalHeaderLabels([u'Монтер', u'Навык'])
    self.workerTable.horizontalHeader().setResizeMode(QHeaderView.Stretch)
    self.workerTable.verticalHeader().setVisible(False)
    for i, worker in enumerate(self.model.individ.route):
      param = [worker.name.decode('utf-8'), '; '.join(worker.skill)]
      for j, p in enumerate(param):
        item = QTableWidgetItem('%s' % (p))
        self.workerTable.setItem(i, j, item)

    taskRows = self.model.graph.get_vertex_count()
    taskCols = 5
    self.taskTable.setRowCount(taskRows)
    self.taskTable.setColumnCount(taskCols)
    self.taskTable.setHorizontalHeaderLabels([u'Адрес', u'Тип проблемы',
                                              u'Приоритет',
                                              u'Времени прибытия'])
    self.workerTable.horizontalHeader().setResizeMode(QHeaderView.Stretch)
    self.taskTable.verticalHeader().setVisible(False)
    unClient = get_unvisit_client(self.model.individ, self.model.graph)
    for k, task in enumerate(self.model.graph):
      if not task.data._isBase:
        param = [task.data._address,
                 '; '.join(task.data._taskType),
                 task.data._prior,
                 '{0} - {1}'.format(task.data._startArrive, task.data._endArrive)]
        for m, p in enumerate(param):
          item = QTableWidgetItem('%s' % (p))
          if task in unClient:
            item.setData(Qt.BackgroundRole, QColor('red'))

          self.taskTable.setItem(k, m, item)

  def update(self):
    self.graphic.repaint()

class WebMap(QWidget):
  def __init__(self, parent=None):
    QWidget.__init__(self, parent)
    self.viewer = QWebView(self)
    self.viewer.setMinimumSize(200, 150)
    self.viewer.load(QUrl(MAP))
    self.button = Tool(self)

    self.layout = QVBoxLayout(self)
    self.layout.stretch(6)
    self.layout.addWidget(self.viewer)
    self.layout.addWidget(self.button)

    self.button.button.clicked.connect(self.push)

  def push(self):
    self.printer = QPrinter(QPrinterInfo.defaultPrinter(),QPrinter.HighResolution)
    self.printer.setOutputFormat(QPrinter.PdfFormat)
    self.printer.setOrientation(QPrinter.Portrait)
    self.printer.setPaperSize(QPrinter.A4)
    self.printer.setFullPage(True)
    filename = QFileDialog.getSaveFileName(self, 'Save file', '', '.pdf')
    #self.printer.setResolution(72)
    self.printer.setOutputFileName(filename)
    self.viewer.print_(self.printer)


class Tool(QWidget):
  def __init__(self, parent=None):
    QWidget.__init__(self, parent)
    self.button = QPushButton('Save', self)
    self.l = QHBoxLayout(self)
    self.l.addStretch(1)
    self.l.addWidget(self.button)


class Graphic(QWidget):
  def __init__(self, data, parent=None):
    QWidget.__init__(self, parent)
    self.setMinimumSize(300, 200)
    self.model = data
    self.updateSteps()

  def paintEvent(self, event):
    qp = QPainter()
    qp.begin(self)
    self.paintGraphic(qp)
    qp.end()

  def paintGraphic(self, qp):
    self.updateSteps()
    pen = QPen(QColor(0, 0, 0))
    dashPen = QPen(Qt.DashDotDotLine)
    qp.setPen(pen)
    qp.drawLine(self.width() - self.widthG, self.height() - self.indentY,
                self.width() - 10, self.height() - self.indentY)
    qp.drawLine(self.width() - self.widthG, self.height() - self.indentY,
                self.width() - self.widthG, self.indentY)
    qp.setPen(dashPen)
    offset = self.width() - self.widthG
    for i, time in enumerate(self.model.timeline):
      notchX = offset + self.stepX*i
      qp.drawLine(notchX, self.height() - self.indentY, notchX, self.indentY)
      metrics = qp.fontMetrics()
      fw = metrics.width(str(time))
      qp.drawText(notchX - fw/2, self.height() - self.indentY + 13, str(time))

    for i, worker in enumerate(self.model.individ.route):
      qp.setPen(dashPen)
      notchY = self.height() - self.indentY - self.stepY * i
      qp.drawLine(offset, notchY, self.width() - 10, notchY)
      workerName = qp.fontMetrics()
      name = worker.name.decode('utf-8')
      fw = workerName.width(name)
      qp.drawText(offset - fw, notchY - self.stepY/2, name)


      tA, tT = self.model.timeArrive(worker)
      assert isinstance(tA, object)

      for i, j in zip(tA, tT):
        obj = TimeRect(offset + (i - 8)*self.stepX, notchY - self.stepY,
                       self.stepX * j, self.stepY)
        obj.paint(qp)


  def updateSteps(self):
    size = self.size()
    w = size.width()
    h = size.height()
    self.widthG = w * 0.9
    self.stepX =int(round((self.widthG - 10) / float(len(self.model.timeline))))
    self.indentY = int(round(self.height() / 10.0))
    self.heightG = h - self.indentY*2
    self.stepY = int(round(self.heightG / len(self.model.individ.route)))

class Controller(object):
  def __init__(self, model):
    self._model = model
    self._view = View(self, model)
    self._view.show()

  def changePos(self):
    pass


if __name__ == '__main__':
  app = QApplication(sys.argv)
  # создаём модель
  model = Model()

  # создаём контроллер и передаём ему ссылку на модель
  controller = Controller(model)
  sys.exit(app.exec_())