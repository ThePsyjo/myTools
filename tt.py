#!/usr/bin/env python2
#################################
# tt.py	TimeTrack		#
#				#
# Copyright 2012 ThePsyjo	#
#				#
# distributed under the terms	#
# of the			#
# GNU General Public License v2	#
#################################
# backup:
# echo ".dump tt" | sqlite3 .tt.db | gzip -f - > $(date +tt_%Y%m%d_%H.sql.gz)
import sys
import os
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QTimer,SIGNAL, SLOT, pyqtSlot, QDateTime, QStringList
from PyQt4.QtGui import QMainWindow, QWidget, QStatusBar, QLineEdit, QGridLayout, QMessageBox, QLabel, QPushButton, QHBoxLayout, QDateTimeEdit, QVBoxLayout, QCompleter

import sqlite3
from datetime import datetime
from time import mktime
import re


class TplRow(QWidget):
	def __init__(self, parent = None, _id = 0):
		super(TplRow, self).__init__(parent)
		self.id = _id
		self.setLayout(QHBoxLayout())
		self.idLabel = QLabel(self)
		self.beginEdit = QDateTimeEdit(self)
		self.beginEdit.setCalendarPopup(True) 
		self.endEdit = QDateTimeEdit(self)
		self.endEdit.setCalendarPopup(True)
		self.descriptionEdit = QLineEdit(self)
		self.noteEdit = QLineEdit(self)
		self.delButton = QPushButton(self)
		self.delButton.setText('X')
		
		self.layout().addWidget(self.idLabel)
		self.layout().addWidget(self.beginEdit)
		self.layout().addWidget(self.endEdit)
		self.layout().addWidget(self.descriptionEdit)
		self.layout().addWidget(self.noteEdit)
		self.layout().addWidget(self.delButton)
		
		self.connect(self.descriptionEdit, SIGNAL('editingFinished ()'), self.notify)
		self.connect(self.noteEdit, SIGNAL('editingFinished ()'), self.notify)
		self.connect(self.beginEdit, SIGNAL('editingFinished ()'), self.notify)
		self.connect(self.endEdit, SIGNAL('editingFinished ()'), self.notify)
		self.connect(self.delButton, SIGNAL('clicked()'), self.delete)
		
	def set(self, tpl):
		self.idLabel.setText(str(tpl[0]))
		self.beginEdit.setDateTime(QDateTime.fromTime_t(tpl[1]))
		self.endEdit.setDateTime(QDateTime.fromTime_t(tpl[2]))
		self.descriptionEdit.setText(tpl[3])
		self.noteEdit.setText(tpl[4])
	
	def get(self):
		tpl = []
		tpl.append(int(self.idLabel.text()))
		tpl.append(self.beginEdit.dateTime().toTime_t())
		tpl.append(self.endEdit.dateTime().toTime_t())
		tpl.append(self.descriptionEdit.text())
		tpl.append(self.noteEdit.text())
		return tpl
	
	def clear(self):
		self.beginEdit.clear()
		self.endEdit.clear()
		self.descriptionEdit.clear()
		self.noteEdit.clear()
		self.idLabel.clear()

	@pyqtSlot()
	def delete(self):
		if self.idLabel.text():
			if QMessageBox.question(self, 'delete ?', 'really delete id %s ?' % self.idLabel.text(), QMessageBox.Yes|QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
				self.emit(SIGNAL('del(int)'), self.id)

	@pyqtSlot()
	def notify(self):
		if self.idLabel.text():
			self.emit(SIGNAL('valueChanged(int)'), self.id)
		
class TplTable(QWidget):
	def __init__(self, parent = None, size = 10):
		super(TplTable, self).__init__(parent)
		
		self.size = size
		self.setLayout(QVBoxLayout())
		
		self.rows = {}
		for n in range(self.size):
			self.rows[n] = TplRow(self, n)
			self.layout().addWidget(self.rows[n])
			self.connect(self.rows[n], SIGNAL('valueChanged(int)'), self.notify)
			self.connect(self.rows[n], SIGNAL('del(int)'), self.delete)
			
	def set(self, data):
		for n in range(self.size):
			try:
				self.rows[n].set(data[n])
			except:
				self.rows[n].clear()
	
	def get(self, _id):
		return self.rows[_id].get()
	
	def getFirstId(self):
		try:
			return int(self.rows[0].get()[0])
		except:
			return 0
		
	def getLastId(self):
		_id = 0
		for rId in self.rows:
			try:
				_id = int(self.rows[rId].get()[0])
			except:
				break
		return _id
	
	def getFirstTime(self):
		try:
			return int(self.rows[0].get()[1])
		except:
			return 0
		
	def getLastTime(self):
		_time = 0
		for rId in self.rows:
			try:
				_time = int(self.rows[rId].get()[1])
			except:
				break
		return _time
		
	@pyqtSlot()
	def delete(self, _id):
		self.emit(SIGNAL('del(int)'), _id)
			
	@pyqtSlot()
	def notify(self, _id):
		self.emit(SIGNAL('valueChanged(int)'), _id)

class MainWindow(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		
		self.listSize = 15
		self.verbose = False

		self.timePattern = re.compile('\.[0-9]+$')
		
		self.setWindowTitle('%s %s' % (QApplication.applicationName(), QApplication.applicationVersion()));
		
		self.widget = QWidget()
		self.setCentralWidget(self.widget)

		self.statusBar = QStatusBar(self)
		self.setStatusBar(self.statusBar)

		self.mAction = self.menuBar().addMenu(self.tr("&Action"))
		#self.mAction.addAction(self.tr("&update"), self.updateTplTable(), QKeySequence('F5'))
		self.mAction.addAction(self.tr("e&xit"), self.onExit, 'Ctrl+Q')

		self.mAbout = self.menuBar().addMenu(self.tr("&about"))
		self.mAbout.addAction(QApplication.applicationName(), self.onAboutAppAction)
		self.mAbout.addAction("Qt", self.onAboutQtAction)
		
		self.pageForwardButton = QPushButton(self)
		self.pageForwardButton.setText('>')
		self.connect(self.pageForwardButton, SIGNAL('clicked()'), self.pageForward)

		self.pageBackwardButton = QPushButton(self)
		self.pageBackwardButton.setText('<')
		self.connect(self.pageBackwardButton, SIGNAL('clicked()'), self.pageBackward)
		
		self.timer = QTimer(self)
		self.timer.setInterval(1000)
		self.connect(self.timer, SIGNAL('timeout()'), self, SLOT('onTimer()'))
		self.time_begin = datetime.now()
		self.time_end = datetime.now()

		db_path = os.path.join(os.path.dirname(sys.argv[0]) if os.name != 'posix' else os.path.expanduser('~'), '.tt.db')
		self.db = sqlite3.connect(db_path)
		self.cursor = self.db.cursor()
		
		try:
			self.cursor.execute('SELECT id FROM tt LIMIT 1')
		except:
			self.createDb()
		
		self.layout = QGridLayout(self.widget)
		
		self.descriptionLabel = QLabel(self.widget)
		self.descriptionLabel.setText('Beschreibung')
		self.descriptionInput = QLineEdit(self.widget)
		self.updateDescriptionEditCompleter()				
		self.noteLabel = QLabel(self.widget)
		self.noteLabel.setText('Notiz')
		self.noteInput = QLineEdit(self.widget)
		self.startStopButton = QPushButton(self.widget)
		self.startStopButton.setText('Start')
		
		self.tableView = TplTable(self, self.listSize)
		
		self.updateTplTable()
			
		self.layout.addWidget(self.descriptionLabel, 0, 0, 1, 1)
		self.layout.addWidget(self.descriptionInput, 1, 0, 1, 1)
		self.layout.addWidget(self.noteLabel, 0, 1, 1, 1)
		self.layout.addWidget(self.noteInput, 1, 1, 1, 1)
		self.layout.addWidget(self.startStopButton, 2, 0, 1, 2)
		self.layout.addWidget(self.tableView, 3,0,1,2)
		self.layout.addWidget(self.pageBackwardButton, 4, 0, 1, 1)
		self.layout.addWidget(self.pageForwardButton, 4, 1, 1, 1)

		self.connect(self.descriptionInput, SIGNAL('returnPressed ()'), self.onStartStop )
		self.connect(self.startStopButton, SIGNAL('clicked()'), self.onStartStop )
		self.connect(self.tableView, SIGNAL('valueChanged(int)'), self.onValueChanged )
		self.connect(self.tableView, SIGNAL('del(int)'), self.onDelete )
		
	def __del__(self):
		pass
	
	def createDb(self):
		try:
			self.q('''CREATE TABLE tt (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			time_begin INTEGER,
			time_end INTEGER,
			description STRING,
			note STRING DEFAULT ""
			)''')
			self.q('CREATE INDEX idx_time_begin ON tt (time_begin)')
		except:
			self.statusBar.showMessage('error creating Database!')
		else:
			self.statusBar.showMessage('Database tt created successfully')
			
	def q(self, query):
		try:
			self.cursor.execute(query)
		except:
			self.statusBar.showMessage('query execution failed "%s"' % query)
		else:
			self.db.commit()
	
	def updateTplTable(self):
		self.q('SELECT * FROM tt ORDER BY time_begin DESC LIMIT %d' % ( self.listSize ) )
		self.tableView.set(self.cursor.fetchall())
		
	def updateDescriptionEditCompleter(self):
		self.q('SELECT DISTINCT description FROM tt')
		words = QStringList()
		for word in self.cursor.fetchall():
			words.append(word[0])
		self.descriptionInput.setCompleter(QCompleter(words, self))

	@pyqtSlot()
	def pageForward(self):
		self.q('SELECT MIN(time_begin) FROM tt')
		if not self.tableView.getLastTime() == self.cursor.fetchone()[0]:
			sql = 'SELECT * FROM tt WHERE time_begin < %d  ORDER BY time_begin DESC LIMIT %s' % ( self.tableView.getLastTime(), self.listSize)
			if self.verbose:
				print( sql )
			self.q( sql )
			self.tableView.set(self.cursor.fetchall())

	@pyqtSlot()
	def pageBackward(self):
		self.q('SELECT MAX(time_begin) FROM tt')
		if not self.tableView.getFirstTime() == self.cursor.fetchone()[0]:
			sql = 'SELECT * FROM ( SELECT * FROM tt WHERE time_begin > %d ORDER BY time_begin LIMIT %s ) as tbl ORDER BY time_begin DESC' % ( self.tableView.getFirstTime(), self.listSize)
			if self.verbose:
				print( sql )
			self.q( sql )
			self.tableView.set(self.cursor.fetchall())
		
	@pyqtSlot()
	def onExit(self):
		QApplication.exit();

	@pyqtSlot()
	def onValueChanged(self, _id):
		if self.verbose:
			print 'changed:', _id
			print self.tableView.get(_id)
		data = self.tableView.get(_id)
		self.q('''
				UPDATE tt
				SET time_begin = %d,
				time_end = %d,
				description = '%s',
				note = '%s'
				WHERE
				id = %d
				'''	% ( data[1], data[2], data[3], data[4], data[0] ))
		self.updateDescriptionEditCompleter()				

	@pyqtSlot()
	def onDelete(self, _id):
		if self.verbose:
			print 'del:', _id,self.tableView.get(_id)[0]
		self.q('DELETE FROM tt WHERE id = %d' % self.tableView.get(_id)[0])
		self.updateTplTable()
		self.updateDescriptionEditCompleter()				
		
	@pyqtSlot()
	def onTimer(self):
		self.startStopButton.setText('Stop (%s)' % self.timePattern.sub( '', str( datetime.now() - self.time_begin ) ) )

	@pyqtSlot()
	def onStartStop(self):
		if self.timer.isActive():
			self.timer.stop()
			self.time_end = datetime.now()
			self.q('''
				INSERT INTO tt
				(time_begin,time_end,description,note)
				VALUES
				('%d','%d','%s','%s')
				'''	% ( int(mktime(self.time_begin.timetuple())), int(mktime(self.time_end.timetuple())), self.descriptionInput.text(), self.noteInput.text() ))
			self.noteInput.clear()
			self.updateTplTable()
			self.updateDescriptionEditCompleter()				
			self.startStopButton.setText('Start')
		else:
			self.time_begin = datetime.now()
			self.timer.start()
			self.onTimer()

	def onAboutAppAction(self):
		QMessageBox.about(self, self.tr("&about"), self.tr("name %1 version %2").arg(QApplication.applicationName()).arg(QApplication.applicationVersion()))
		
	def onAboutQtAction(self):
		QMessageBox.aboutQt(self, self.tr("&about"))


app = QApplication(sys.argv)

app.setApplicationName('TimeTrack')
app.setApplicationVersion('0.1.2')
app.setQuitOnLastWindowClosed(True)

w = MainWindow()
w.show()

sys.exit(app.exec_())
