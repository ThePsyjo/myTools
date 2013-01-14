#!/usr/bin/env python2
#################################
# tt2.py TimeTrack v2           #
#                               #
# Copyright 2012 ThePsyjo       #
#                               #
# distributed under the terms   #
# of the                        #
# GNU General Public License v2 #
#################################
# backup:
# echo ".dump tt" | sqlite3 .tt2.db | gzip -f - > $(date +tt2_%Y%m%d_%H.sql.gz)
import sys
import os
from PyQt4.QtCore import QTimer,SIGNAL, SLOT, pyqtSlot, pyqtSignal, QDateTime, QStringList, Qt
from PyQt4.QtGui import QApplication, QMainWindow, QWidget, QStatusBar, QLineEdit, QGridLayout, QMessageBox, QLabel, QPushButton, QHBoxLayout, QDateTimeEdit, QVBoxLayout, QCompleter, QGroupBox, QFont, QKeySequence, QAction, QMouseEvent, QDialog

import sqlite3
from datetime import datetime
from time import mktime, sleep
import re
from math import ceil
import requests
from json import dumps as jsondumps
from threading import Thread, Timer

class ClickLabel( QLabel ):
	def __init__(self, parent = None):
		super(ClickLabel, self).__init__(parent)

	def mousePressEvent ( self, QMouseEvent ):
		self.emit( SIGNAL( 'clicked()' ) )

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
		self.timeDiff = ClickLabel(self)
		self.descriptionEdit = QLineEdit(self)
		self.noteEdit = QLineEdit(self)
		self.delButton = QPushButton(self)
		self.delButton.setText('X')
		
		self.layout().addWidget(self.idLabel)
		self.layout().addWidget(self.beginEdit)
		self.layout().addWidget(self.endEdit)
		self.layout().addWidget(self.timeDiff)
		self.layout().addWidget(self.descriptionEdit)
		self.layout().addWidget(self.noteEdit)
		self.layout().addWidget(self.delButton)

		self.layout().setContentsMargins(2,2,2,2)
		
		self.connect(self.descriptionEdit, SIGNAL('editingFinished ()'), self.notify)
		self.connect(self.noteEdit, SIGNAL('editingFinished ()'), self.notify)
		self.connect(self.beginEdit, SIGNAL('editingFinished ()'), self.notify)
		self.connect(self.endEdit, SIGNAL('editingFinished ()'), self.notify)
		self.connect(self.delButton, SIGNAL('clicked()'), self.delete)
		self.connect(self.timeDiff, SIGNAL('clicked()'), self.onTimeDiff)

	def set(self, tpl):
		self.idLabel.setText(str(tpl[0]))
		self.beginEdit.setDateTime(QDateTime.fromTime_t(tpl[1]))
		self.endEdit.setDateTime(QDateTime.fromTime_t(tpl[2]))
		self.timeDiff.setText( self.mkDiff( tpl[1], tpl[2] ) )
		self.descriptionEdit.setText(str(tpl[3]))
		self.noteEdit.setText(str(tpl[4]))
	
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
		self.timeDiff.clear()
		self.descriptionEdit.clear()
		self.noteEdit.clear()
		self.idLabel.clear()

	def mkDiff(self, begin, end):
		return '%4d' % ceil( float( end - begin ) / 60 )

	@pyqtSlot()
	def onTimeDiff(self):
		self.parent().parent().parent().statusBar.showMessage( '%s copied to clipboard.' % self.timeDiff.text() )
		self.parent().clipboard.setText( str(self.timeDiff.text()).strip() )

	@pyqtSlot()
	def delete(self):
		if self.idLabel.text():
			if QMessageBox.question(self, 'delete ?', 'really delete id %s ?' % self.idLabel.text(), QMessageBox.Yes|QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
				self.emit(SIGNAL('del(int)'), self.id)

	@pyqtSlot()
	def notify(self):
		if self.idLabel.text():
			self.timeDiff.setText( self.mkDiff( self.beginEdit.dateTime().toTime_t(), self.endEdit.dateTime().toTime_t() ) )
			self.emit(SIGNAL('valueChanged(int)'), self.id)
		
class TplTable(QGroupBox):
	def __init__(self, parent = None, size = 10):
		super(TplTable, self).__init__(parent)
		
		self.size = size
		self.setLayout(QVBoxLayout())
		self.layout().setSpacing(2)
		self.clipboard = QApplication.clipboard()
		
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

class SettingsWidget(QDialog):
	def __init__(self, defaults = {}, parent = None):
		QDialog.__init__(self)
		self.setParent(parent)
		self.setWindowFlags(Qt.Dialog)
		self.setWindowTitle(self.tr('settings'))
		self.setModal(1)
		self.defaults = defaults

		self.urlLabel = QLabel(self)
		self.urlLabel.setText('RESR URL (including trailing / !)')
		self.urlLabel.setMaximumHeight( self.font().pointSize() * 2 )
		self.urlInput = QLineEdit(self)
		self.urlInput.setText( self.get( 'url' ) )

		self.userLabel = QLabel(self)
		self.userLabel.setText('username')
		self.userLabel.setMaximumHeight( self.font().pointSize() * 2 )
		self.userInput = QLineEdit(self)
		self.userInput.setText( self.get( 'username' ) )
		
		self.passwordLabel = QLabel(self)
		self.passwordLabel.setText('password')
		self.passwordLabel.setMaximumHeight( self.font().pointSize() * 2 )
		self.passwordInput = QLineEdit(self)
		self.passwordInput.setEchoMode( QLineEdit.Password )
		self.passwordInput.setText( self.get( 'password' ) )

		self.okButton = QPushButton(self)
		self.okButton.setText( 'OK' )
		self.connect(self.okButton, SIGNAL('clicked()'), self.ok)
		self.checkButton = QPushButton(self)
		self.checkButton.setText( 'Check' )
		self.connect(self.checkButton, SIGNAL('clicked()'), self.check)

		self.layout = QGridLayout(self)

		self.layout.addWidget( self.urlLabel, 0, 0 )
		self.layout.addWidget( self.urlInput, 0, 1 )
		self.layout.addWidget( self.userLabel, 1, 0 )
		self.layout.addWidget( self.userInput, 1, 1 )
		self.layout.addWidget( self.passwordLabel, 2, 0 )
		self.layout.addWidget( self.passwordInput, 2, 1 )

		self.layout.addWidget( self.okButton, 3, 0 )
		self.layout.addWidget( self.checkButton, 3, 1 )

	def get(self, key):
		try:
			v = self.defaults[key]
		except:
			v = ''
		return v

	def ok(self):
		self.accept()

	def check(self):
		url = '%s1' % self.urlInput.text()
		r = requests.get(url, auth=( self.userInput.text(), self.passwordInput.text() ) )
		if r.status_code in [200,404]:
			for itm in [ self.urlInput, self.userInput, self.passwordInput ]:
				itm.setStyleSheet( 'background-color: green' )
		else:
			for itm in [ self.urlInput, self.userInput, self.passwordInput ]:
				itm.setStyleSheet( 'background-color: red' )

	def data(self):
		return {'url' : self.urlInput.text(), 'username' : self.userInput.text(), 'password' : self.passwordInput.text()}

class MainWindow(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		
		self.listSize = 20
		self.verbose = False
		self.sync_active = False
		self.sync_waiting = False

		self.timePattern = re.compile('\.[0-9]+$')
		
		self.setWindowTitle('%s %s' % (QApplication.applicationName(), QApplication.applicationVersion()));
		
		self.widget = QWidget()
		self.setCentralWidget(self.widget)

		self.statusBar = QStatusBar(self)
		self.setStatusBar(self.statusBar)

		self.mAction = self.menuBar().addMenu(self.tr("&Action"))
		#self.mAction.addAction(self.tr("&update"), self.updateTplTable(), QKeySequence('F5'))
		self.mAction.addAction(self.tr('edit settings'), self.onSettings, QKeySequence('F8'))
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

		self.db_path = os.path.join(os.path.dirname(sys.argv[0]) if os.name != 'posix' else os.path.expanduser('~'), '.tt2.db')
		self.db = sqlite3.connect(self.db_path)
		self.cursor = self.db.cursor()
		
		try:
			self.cursor.execute('SELECT id FROM tt LIMIT 1')
		except:
			self.createDb()
		
		self.layout = QGridLayout(self.widget)
		
		self.descriptionLabel = QLabel(self.widget)
		self.descriptionLabel.setText('Beschreibung')
		self.descriptionLabel.setMaximumHeight( self.font().pointSize() * 2 )
		self.descriptionInput = QLineEdit(self.widget)
		self.updateDescriptionEditCompleter()				
		self.noteLabel = QLabel(self.widget)
		self.noteLabel.setText('Notiz')
		self.noteLabel.setMaximumHeight( self.font().pointSize() * 2 )
		self.noteInput = QLineEdit(self.widget)
		self.startStopButton = QPushButton(self.widget)
		self.startStopButton.setText('Start')
		
		self.tableView = TplTable(self, self.listSize)

		self.pageForwardAction = QAction(self)
		self.pageForwardAction.setShortcut(QKeySequence('Right'))
		self.connect(self.pageForwardAction, SIGNAL('triggered()'), self.pageForward);
		self.pageForwardButton.addAction(self.pageForwardAction)

		self.pageBackwardAction = QAction(self)
		self.pageBackwardAction.setShortcut(QKeySequence('Left'))
		self.connect(self.pageBackwardAction, SIGNAL('triggered()'), self.pageBackward);
		self.pageBackwardButton.addAction(self.pageBackwardAction)

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
		self.connect(self.noteInput, SIGNAL('returnPressed ()'), self.onStartStop )
		self.connect(self.startStopButton, SIGNAL('clicked()'), self.onStartStop )
		self.connect(self.tableView, SIGNAL('valueChanged(int)'), self.onValueChanged )
		self.connect(self.tableView, SIGNAL('del(int)'), self.onDelete )

		self.sync()
	
	def __del__(self):
		pass

	def sync(self):
		if self.sync_active:
			try:
				self.t.cancel()
			except:
				pass
			self.t = Timer(10,self.sync)
			self.t.start()
		else:
			Thread(target=self.do_sync).start()

	def do_sync(self):
		self.sync_active = True
		try:
			db = sqlite3.connect(self.db_path)
			cursor = db.cursor()

			def q(query):
				try:
					cursor.execute(query)
				except:
					self.statusBar.showMessage('query execution failed "%s"' % query)
				else:
					db.commit()
			
			settings = {}
			q( 'SELECT * FROM settings' )
			for row in cursor.fetchall():
				settings[row[0]] = row[1]

			#print 'new'
			# update new
			q('SELECT id,time_begin,time_end,description,note FROM tt WHERE is_new = 1')
			for row in cursor.fetchall():

				url = '%s0' % settings['url']
				data = {'note': row[4], 'description': row[3], 'time_end': row[2], 'time_begin': row[1]}

				r = requests.post(url, auth=(settings['username'], settings['password']), data = data)

				if r.status_code == 201:
					#print 'n',r.json['data']['id']
					q( 'UPDATE tt SET remote_id = %s WHERE id = %d' % ( r.json['data']['id'], row[0] ) )
					q( 'UPDATE tt SET is_new = 0 WHERE id = %d' % row[0] )

			#print 'update'
			# update
			q('SELECT id,time_begin,time_end,description,note,remote_id FROM tt WHERE need_update = 1')
			for row in cursor.fetchall():

				url = '%s%d' % ( settings['url'], row[5] )
				data = {'note': row[4], 'description': row[3], 'time_end': row[2], 'time_begin': row[1]}

				r = requests.put(url, auth=(settings['username'], settings['password']), data = data)

				if r.status_code == 200:
					#print 'u',row[0]
					q( 'UPDATE tt SET need_update = 0 WHERE id = %d' % row[0] )

			#print 'del'
			# delete
			q('SELECT id,remote_id FROM tt WHERE is_delete = 1')
			for row in cursor.fetchall():
				url = '%s%d' % ( settings['url'], row[1] )
				r = requests.delete(url, auth=(settings['username'], settings['password']))
				if r.status_code in [ 200, 404 ]:
					#print 'd',row[0]
					q( 'DELETE FROM tt WHERE id = %s' % row[0] )
		except Exception, e:
			#print( 'Syncer cought an error:\n', e )
			pass

		self.sync_active = False

	def createDb(self):
		try:
			self.q('''CREATE TABLE tt (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			remote_id INTEGER,
			time_begin INTEGER,
			time_end INTEGER,
			description STRING,
			note STRING DEFAULT "",
			is_new INTEGER DEFAULT 1,
			need_update INTEGER DEFAULT 0,
			is_delete INTEGER DEFAULT 0
			)''')
			self.q('''CREATE TABLE settings (
			key STRING UNIQUE,
			value STRING
			)''')
			self.q('CREATE INDEX idx_time_begin ON tt (time_begin)')
		except:
			self.statusBar.showMessage('error creating Database!')
		else:
			self.statusBar.showMessage('Table tt created successfully')
			
	def q(self, query):
		try:
			self.cursor.execute(query)
		except:
			self.statusBar.showMessage('query execution failed "%s"' % query)
		else:
			self.db.commit()
	
	def updateTplTable(self):
		self.q('SELECT id,time_begin,time_end,description,note FROM tt WHERE is_delete != 1 ORDER BY time_begin DESC LIMIT %d' % ( self.listSize ) )
		self.tableView.set(self.cursor.fetchall())
		
	def updateDescriptionEditCompleter(self):
		self.q('SELECT DISTINCT description FROM tt WHERE is_delete != 1')
		words = QStringList()
		for word in self.cursor.fetchall():
			words.append(unicode(word[0]))
		self.descriptionInput.setCompleter(QCompleter(words, self))

	@pyqtSlot()
	def pageForward(self):
		self.q('SELECT MIN(time_begin) FROM tt')
		if not self.tableView.getLastTime() == self.cursor.fetchone()[0]:
			sql = 'SELECT id,time_begin,time_end,description,note FROM tt WHERE is_delete != 1 AND time_begin < %d ORDER BY time_begin DESC LIMIT %s' % ( self.tableView.getLastTime(), self.listSize)
			if self.verbose:
				print( sql )
			self.q( sql )
			self.tableView.set(self.cursor.fetchall())

	@pyqtSlot()
	def pageBackward(self):
		self.q('SELECT MAX(time_begin) FROM tt')
		if not self.tableView.getFirstTime() == self.cursor.fetchone()[0]:
			sql = 'SELECT * FROM ( SELECT id,time_begin,time_end,description,note FROM tt WHERE is_delete != 1 AND time_begin > %d ORDER BY time_begin LIMIT %s ) as tbl ORDER BY time_begin DESC' % ( self.tableView.getFirstTime(), self.listSize)
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
				note = '%s',
				need_update = 1
				WHERE
				id = %d
				'''	% ( data[1], data[2], data[3], data[4], data[0] ))
		self.updateDescriptionEditCompleter()
		self.sync()

	@pyqtSlot()
	def onDelete(self, _id):
		if self.verbose:
			print 'del:', _id,self.tableView.get(_id)[0]
		self.q('UPDATE tt SET is_delete = 1 WHERE id = %d' % self.tableView.get(_id)[0])
		self.updateTplTable()
		self.updateDescriptionEditCompleter()				
		self.sync()
		
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
			self.sync()
		else:
			self.time_begin = datetime.now()
			self.timer.start()
			self.onTimer()

	def onAboutAppAction(self):
		QMessageBox.about(self, self.tr("&about"), self.tr("%1 version %2").arg(QApplication.applicationName()).arg(QApplication.applicationVersion()))
		
	def onAboutQtAction(self):
		QMessageBox.aboutQt(self, self.tr("&about"))

	def onSettings(self):
		settings = {}
		self.q( 'SELECT * FROM settings' )
		for row in self.cursor.fetchall():
			settings[row[0]] = row[1]

		inp = SettingsWidget(settings, self)
		if inp.exec_():
			self.q( '''REPLACE INTO settings VALUES ('url','%s')''' % inp.data()['url'] )
			self.q( '''REPLACE INTO settings VALUES ('username','%s')''' % inp.data()['username'] )
			self.q( '''REPLACE INTO settings VALUES ('password','%s')''' % inp.data()['password'] )

app = QApplication(sys.argv)

app.setApplicationName('TimeTrack2 !!!! TEST !!!!')
app.setApplicationVersion('1.0.0')
app.setQuitOnLastWindowClosed(True)

w = MainWindow()
w.show()

sys.exit(app.exec_())
