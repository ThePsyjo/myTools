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

if  sys.version_info < (3,0):
	print ('Python is too old here. Upgrade at least to 3.0!')
	sys.exit(1);

import os
from PyQt4.QtCore import QTimer,SIGNAL, SLOT, pyqtSlot, QDateTime, Qt, QObject
from PyQt4.QtGui import QApplication, QMainWindow, QWidget, QStatusBar, QLineEdit, QGridLayout, QMessageBox, QLabel, QPushButton, QHBoxLayout, QDateTimeEdit, QVBoxLayout, QCompleter, QGroupBox, QKeySequence, QAction, QDialog, QCheckBox, QSpinBox, QProgressBar, QIcon

import sqlite3
from datetime import datetime, timedelta
from time import mktime
import re
from math import ceil
import requests
from threading import Thread, Timer
from zlib import compress, decompress
from base64 import b64encode, b64decode

DEFAULTROWS = 20

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

class WorkerBase(QObject):
	def __init__(self, db_path, parent = None):
		QObject.__init__(self)
		self.setParent = parent
		self.db_path = db_path
		self.initDb()

	def initDb(self):
		self.db = sqlite3.connect(self.db_path)
		self.cursor = self.db.cursor()

	def msg(self, msg, timeout = 0):
		#print msg
		self.emit( SIGNAL("message"), msg, timeout ) 

	def q(self, query, commit = True):
		try:	self.cursor.execute(query)
		except:	self.msg('query execution failed "%s"' % query)
		else:
			if commit:
				self.db.commit()

	def beginTransaction(self):
		self.q( 'BEGIN TRANSACTION' )

	def commit(self):
		self.q( 'COMMIT' )
		self.db.commit()

	def fetchSettings(self):
		self.settings = {}
		self.q( 'SELECT key, value FROM settings' )
		for key, value in self.cursor.fetchall():
			if key == 'password':
				self.settings[key] = decompress(b64decode(bytes( value, 'UTF-8' ))).decode( 'UTF-8' )
			else:
				self.settings[key] = value

	def getLocalIdList(self):
		self.q('SELECT remote_id FROM tt' )
		return [ itm[0] for itm in self.cursor.fetchall() ]

	def getRemoteIdList(self):
		self.msg( 'get remote records' )
		url = '%s0' % self.settings['url']
		r = requests.get( url, auth=(self.settings['username'], self.settings['password']) )
		if r.status_code == 200:
			l = r.json()['data']
		else:
			l = []
		return l

	def getMissingRemoteIdList(self):
		import_ids = []
		local_ids = self.getLocalIdList()
		self.msg( 'check missing' )
		for remote_id in self.getRemoteIdList():
			if remote_id not in local_ids:
				import_ids.append(remote_id)
		return import_ids

	def getDeletedRemoteIdList(self):
		delete_ids = []
		remote_ids = self.getRemoteIdList()
		self.msg( 'check deleted' )
		for remote_id in self.getLocalIdList():
			if remote_id not in remote_ids:
				delete_ids.append(remote_id)
		return delete_ids

	def getRecords(self, fields, where):
		l = []
		self.q('SELECT %s FROM tt %s' % ( ','.join( fields ), where ) )
		while True:
			row = self.cursor.fetchone()
			if row == None:
				break
			tpl = {}
			for n in range( len( fields ) ):
				tpl[ fields[ n ] ] = row[ n ]
			l.append(tpl)
		return l

	def getNewRecords(self):
		return self.getRecords( [ 'id','time_begin','time_end','description','note' ], 'WHERE is_new = 1' )

	def getUpdatedRecords(self):
		return self.getRecords( [ 'id', 'remote_id','time_begin','time_end','description','note' ], 'WHERE need_update = 1' )

	def getDeletedRecords(self):
		return self.getRecords( [ 'id', 'remote_id' ], 'WHERE is_delete = 1' )

	def postRecord(self, record):
		record_id = record.pop( 'id' )
		self.msg('send #%d' % record_id)
		url = '%s0' % self.settings['url']
		r = requests.post(url, auth=(self.settings['username'], self.settings['password']), data = record)
		
		if r.status_code == 201:
			self.q( 'UPDATE tt SET remote_id = %s WHERE id = %d' % ( r.json()['data']['id'], record_id ), False )
			self.q( 'UPDATE tt SET is_new = 0 WHERE id = %d' % record_id, False )
			self.msg('send #%d (#%s) ok' % ( record_id, r.json()['data']['id'] ) )

	def updateRecord(self, record):
		record_id = record.pop( 'id' )
		remote_id = record.pop( 'remote_id' )

		self.msg('update #%d (#%s)' % ( record_id, remote_id ) )
		url = '%s%d' % ( self.settings['url'], remote_id )
		r = requests.put(url, auth=(self.settings['username'], self.settings['password']), data = record)
		if r.status_code == 200:
			self.q( 'UPDATE tt SET need_update = 0 WHERE id = %d' % record_id, False )
			self.msg('update #%d (#%s) ok' % ( record_id, remote_id ) )
		elif r.status_code == 404:
			record['id'] = record_id
			self.postRecord(record)

	def deleteRecord(self, record):
		record_id = record.pop( 'id' )
		remote_id = record.pop( 'remote_id' )

		self.msg('delete #%d (#%s)' % ( record_id, remote_id ) )
		url = '%s%d' % ( self.settings['url'], remote_id )
		r = requests.delete(url, auth=(self.settings['username'], self.settings['password']))
		if r.status_code in [ 200, 404 ]:
			self.q( 'DELETE FROM tt WHERE id = %s' % record_id, False )
			self.msg('delete #%d (#%s) ok' % ( record_id, remote_id ) )
	
	def deleteLocalRecord(self, remote_id):
		self.q( 'UPDATE tt SET is_delete = 1 WHERE remote_id = %d' % remote_id, False )

	def updateLocalRecord(self, record):
		self.q('''
				UPDATE tt
				SET time_begin = %d,
				time_end = %d,
				description = '%s',
				note = '%s',
				need_update = 0,
				is_new = 0,
				WHERE
				id = %d
				'''	% ( record['time_begin'], record['time_end'],record['description'],record['note'] ), False
				)

	def newLocalRecord(self, record):
		self.q('''
			INSERT INTO tt
			(time_begin,time_end,description,note,remote_id,is_new,need_update)
			VALUES
			('%d','%d','%s','%s', %d, 0, 0)
			'''	% ( record['time_begin'], record['time_end'],record['description'],record['note'],record['remote_id'] ), False
			)

	def getRemoteRecord(self, remote_id):
		url = '%s%d' % ( self.settings['url'], remote_id )
		r = requests.get(url, auth=(self.settings['username'], self.settings['password']))
		if r.status_code == 200:
			return r.json()['data']
		elif r.status_code == 404:
			return None
						
class ImportWorker(WorkerBase):
	def __init__(self, db_path, parent = None):
		WorkerBase.__init__(self, db_path, parent)
		self.kill = False
		self.running = False

	def term(self):
		self.kill = True

	def run(self):
		self.running = True
		self.kill = False
		self.initDb()
		self.fetchSettings()

		import_ids = self.getMissingRemoteIdList()
		if len( import_ids ) > 0:
			self.emit( SIGNAL('range'), 0, len( import_ids ) )
		n = 0
		self.beginTransaction()
		for remote_id in import_ids:
			if self.kill:break
			self.msg( 'import %d' % remote_id )
			n += 1
			self.emit( SIGNAL('statusChanged'), n ) 
			record = self.getRemoteRecord( remote_id )
			del record['id'] # remote id from server
			record['remote_id'] = remote_id
			self.newLocalRecord( record )
			self.msg( '%d ok' % remote_id )
		self.commit()

		if not self.kill:
			delete_ids = self.getDeletedRemoteIdList()
			if len( delete_ids ) > 0:
				self.emit( SIGNAL('range'), 0, len( delete_ids ) )
			n = 0
			self.beginTransaction()
			for remote_id in delete_ids:
				if self.kill:break
				self.msg( 'delete %d' % remote_id )
				n += 1
				self.emit( SIGNAL('statusChanged'), n ) 
				self.deleteLocalRecord( remote_id )
				self.msg( '%d ok' % remote_id )
			self.commit()

		if self.kill:
			self.msg( 'interrupted' )
		else:
			self.msg( 'done' ) 
			self.emit( SIGNAL('done') )
		self.running = False

class ImportWidget(QDialog):
	def __init__(self, db_path, parent = None):
		QWidget.__init__(self)
		self.setParent(parent)
		self.setWindowFlags(Qt.Dialog)
		self.setWindowTitle(self.tr('Import'))
		self.setModal(1)

		self.startButton = QPushButton(self)
		self.startButton.setText('&start')
		self.connect( self.startButton, SIGNAL('clicked()'), self.onStart )

		self.stopButton = QPushButton(self)
		self.stopButton.setText('&cancel')
		self.stopButton.setEnabled( False )
		self.connect( self.stopButton, SIGNAL('clicked()'), self.onStop )

		self.okButton = QPushButton(self)
		self.okButton.setText('&done')
		self.okButton.setEnabled( False )
		self.connect( self.okButton, SIGNAL('clicked()'), self.onOk )

		self.statusBar = QProgressBar(self)
		self.statusBar.setRange(0, 100)
		self.statusLabel = QLabel(self)

		self.worker = ImportWorker(db_path, self)
		self.connect( self.worker, SIGNAL('statusChanged'), self.statusBar.setValue )
		self.connect( self.worker, SIGNAL('done'), self.onDone )
		self.connect( self.worker, SIGNAL('message'), self.statusLabel.setText )
		self.connect( self.worker, SIGNAL('range'), self.statusBar.setRange )
	
		self.layout = QGridLayout(self)
		self.layout.addWidget( self.startButton, 0, 0 )
		self.layout.addWidget( self.stopButton, 0, 1 )
		self.layout.addWidget( self.okButton, 0, 2 )
		self.layout.addWidget( self.statusBar, 1, 0, 1, 3 )
		self.layout.addWidget( self.statusLabel, 2, 0, 1, 3 )

	def onStart(self):
		self.startButton.setEnabled( False )
		self.stopButton.setEnabled( True )
		self.statusBar.setEnabled( True )
		self.statusLabel.setEnabled( True )
		Thread(target=self.worker.run).start()

	def onDone(self):
		self.okButton.setEnabled( True )
		self.stopButton.setEnabled( False )

	def onStop(self):
		self.worker.term()
		self.statusBar.setEnabled( False )
		self.statusLabel.setEnabled( False )
		self.startButton.setEnabled( True )
		self.stopButton.setEnabled( False )
	
	def onOk(self):
		self.accept()

	def closeEvent(self,event):
		if self.worker.running:
			event.ignore()
		else:
			event.accept()

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

		self.syncLabel = QLabel(self)
		self.syncLabel.setText('enable sync')
		self.syncLabel.setMaximumHeight( self.font().pointSize() * 2 )
		self.syncInput = QCheckBox(self)
		syncEnbl = self.get( 'syncEnabled', 'False' )
		self.syncInput.setChecked(  True if syncEnbl == 'True' else False )
		self.connect(self.syncInput, SIGNAL('clicked()'), self.onSyncInput)

		self.rowLabel = QLabel(self)
		self.rowLabel.setText('display rows (need restart)')
		self.rowLabel.setMaximumHeight( self.font().pointSize() * 2 )
		self.rowInput = QSpinBox(self)
		self.rowInput.setValue(  int( self.get('displayrows', DEFAULTROWS) ) )

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

		self.layout.addWidget( self.syncLabel, 3, 0 )
		self.layout.addWidget( self.syncInput, 3, 1 )

		self.layout.addWidget( self.rowLabel, 4, 0 )
		self.layout.addWidget( self.rowInput, 4, 1 )

		self.layout.addWidget( self.okButton, 5, 0 )
		self.layout.addWidget( self.checkButton, 5, 1 )

		self.onSyncInput()

	def get(self, key, default = None):
		try:
			if key == 'password':
				v = decompress(b64decode(bytes( self.defaults[key], 'UTF-8' ))).decode( 'UTF-8' )
			else:
				v = self.defaults[key]
		except:
			if default != None:
				v = default
			else:
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
	
	def onSyncInput(self):
		for itm in [self.urlLabel, self.urlInput, self.userLabel, self.userInput, self.passwordLabel, self.passwordInput]:
			itm.setEnabled( self.syncInput.isChecked() )

	def data(self):
		return {'url' : self.urlInput.text(), 'username' : self.userInput.text(), 'password' : b64encode(compress(bytes(self.passwordInput.text(), 'UTF-8'))), 'syncEnabled' : self.syncInput.isChecked(), 'displayrows' : self.rowInput.value() }

class Syncer(WorkerBase):
	def __init__(self, db_path, parent = None):
		WorkerBase.__init__(self, db_path, parent)

	def do_sync(self):
		self.emit( SIGNAL("active"), True ) 
		try:
			self.initDb()
			self.fetchSettings()
			self.msg('check for new records')
			self.beginTransaction()
			for record in self.getNewRecords():
				self.postRecord( record )
			self.commit()

			self.msg('check for updated records')
			self.beginTransaction()
			for record in self.getUpdatedRecords():
				self.updateRecord( record )
			self.commit()

			self.msg('check for deleted records')
			self.beginTransaction()
			for record in self.getDeletedRecords():
				self.deleteRecord( record )
			self.commit()

		except Exception as e:
			print( 'Syncer cought an exception:\n%s\n\nDisabling sync.' % e )
			self.q( '''REPLACE INTO settings VALUES ('syncEnabled','False')''' )
			self.commit()
			self.emit( SIGNAL( 'newSettings' ) )

		self.msg('done', 5000)
		self.emit( SIGNAL("active"), False ) 

class MainWindow(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		
		self.sync_delay = 5
		self.sync_active = False
		self.verbose = False

		self.timePattern = re.compile('\.[0-9]+$')
		
		self.setWindowTitle('%s %s' % (QApplication.applicationName(), QApplication.applicationVersion()));
		
		self.widget = QWidget()
		self.setCentralWidget(self.widget)

		self.statusBar = QStatusBar(self)
		self.setStatusBar(self.statusBar)

		self.mAction = self.menuBar().addMenu(self.tr("&Action"))
		#self.mAction.addAction(self.tr("&update"), self.updateTplTable(), QKeySequence('F5'))
		self.mAction.addAction(self.tr('&import records'), self.onImport, QKeySequence('F6'))
		self.mAction.addAction(self.tr('edit &settings'), self.onSettings, QKeySequence('F8'))
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
		
		self.settings = self.fetchSettings()
		self.syncer = Syncer(self.db_path, self)
		self.connect( self.syncer, SIGNAL('active'), self.setSyncerActive )
		self.connect( self.syncer, SIGNAL('message'), self.msg )
		self.connect( self.syncer, SIGNAL('newSettings'), self.fetchSettings )
		
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
		
		self.tableView = TplTable(self, int( self.getSetting('displayrows', DEFAULTROWS) ) )

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

		self.last_sync = datetime.now()
		self.sync()
	
	def __del__(self):
		pass

	def setSyncerActive(self, active):
		if not active:
			self.last_sync = datetime.now()
		self.sync_active = active

	def msg(self, msg, timeout = 0):
		#print(msg)
		self.statusBar.showMessage(msg, timeout)

	def sync(self):
		if self.getSetting('syncEnabled','False') == 'False':
			return

		# reset delay if still active
		if self.sync_active:
			self.last_sync = datetime.now()

		if datetime.now() < ( self.last_sync + timedelta( seconds = self.sync_delay ) ):
			try:
				#print 'cancel'
				self.t.cancel()
			except:
				pass
			#print 'start +',( self.last_sync + timedelta( seconds = self.sync_delay ) - datetime.now() ).seconds + 1
			self.t = Timer( ( self.last_sync + timedelta( seconds = self.sync_delay ) - datetime.now() ).seconds + 1 ,self.sync)
			self.t.start()
		else:
		#	print 'start syncer instance'
			Thread(target=self.syncer.do_sync).start()


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
		except Exception as e:
			print( e )
			self.statusBar.showMessage('query execution failed "%s"' % query)
		else:
			self.db.commit()
	
	def updateTplTable(self):
		self.q('SELECT id,time_begin,time_end,description,note FROM tt WHERE is_delete != 1 ORDER BY time_begin DESC LIMIT %d' % ( int( self.getSetting( 'displayrows', DEFAULTROWS ) ) ) )
		self.tableView.set(self.cursor.fetchall())
		
	def updateDescriptionEditCompleter(self):
		self.q('SELECT DISTINCT description FROM tt WHERE is_delete != 1')
		#words = QStringList()
		words = []
		for word in self.cursor.fetchall():
			words.append(str(word[0]))
		self.descriptionInput.setCompleter(QCompleter(words, self))

	@pyqtSlot()
	def pageForward(self):
		self.q('SELECT MIN(time_begin) FROM tt')
		if not self.tableView.getLastTime() == self.cursor.fetchone()[0]:
			sql = 'SELECT id,time_begin,time_end,description,note FROM tt WHERE is_delete != 1 AND time_begin < %d ORDER BY time_begin DESC LIMIT %s' % ( self.tableView.getLastTime(), int( self.getSetting( 'displayrows', DEFAULTROWS ) ) )
			if self.verbose:
				print( sql )
			self.q( sql )
			self.tableView.set(self.cursor.fetchall())

	@pyqtSlot()
	def pageBackward(self):
		self.q('SELECT MAX(time_begin) FROM tt')
		if not self.tableView.getFirstTime() == self.cursor.fetchone()[0]:
			sql = 'SELECT * FROM ( SELECT id,time_begin,time_end,description,note FROM tt WHERE is_delete != 1 AND time_begin > %d ORDER BY time_begin LIMIT %s ) as tbl ORDER BY time_begin DESC' % ( self.tableView.getFirstTime(), int( self.getSetting( 'displayrows', DEFAULTROWS ) ) )
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
			print('changed:', _id)
			print(self.tableView.get(_id))
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
			print('del:', _id,self.tableView.get(_id)[0])
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

	def checkSync(self):
		if self.sync_active:
			QMessageBox.information(self, 'Information', '''Sync is currently active. Please wait until it's finished''')
			return False
		else:
			return True

	def onSettings(self):
		if not self.checkSync():
			return
		settings = self.fetchSettings()

		inp = SettingsWidget(settings, self)
		if inp.exec_():
			for key in inp.data():
				if type( inp.data()[key] ) == bytes:
					value = inp.data()[key].decode( 'UTF-8' )
				else:
					value = inp.data()[key]
				self.q( '''REPLACE INTO settings VALUES ('%s','%s')''' % ( key, value ) )
			try: dr = settings['displayrows']
			except: dr = None
			if dr != inp.data()['displayrows']:
				QMessageBox.information(self, 'displayrows changed...', 'exiting now.')
				sys.exit(0)
		self.settings = self.fetchSettings()

	def onImport(self):
		if not self.checkSync():
			return
		ImportWidget( self.db_path, self ).exec_()
		self.updateTplTable()
		self.updateDescriptionEditCompleter()				

	def fetchSettings(self):
		s = {}
		self.q( 'SELECT key,value FROM settings' )
		for key,value in self.cursor.fetchall():
			s[key] = value
		return s

	def getSetting(self,key,default = None):
		try:
			v = self.settings[key]
		except:
			if default != None:
				v = default
			else:
				v = ''
		return v

app = QApplication(sys.argv)

app.setApplicationName('TimeTrack2')
#app.setApplicationName('TimeTrack2 !!!! TEST !!!!')
app.setApplicationVersion('1.0.0')
app.setQuitOnLastWindowClosed(True)


w = MainWindow()
icon = os.path.join( os.path.dirname( os.path.abspath( sys.argv[0] ) ), os.path.join( '', 'icon.png' ) )
w.setWindowIcon( QIcon( icon ) )
w.show()

sys.exit(app.exec_())
