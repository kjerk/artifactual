import pathlib
import sys

import PySide6
import requests
from PIL import ImageQt, Image
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QImageReader, QColor
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QTextEdit, QWidget, QSizePolicy, QHBoxLayout, QPushButton, QGraphicsColorizeEffect

import artifactual

class ImageDropArea(QLabel):
	imageDropped = Signal(str)
	
	def __init__(self, parent=None):
		super().__init__(parent)
		# Config properties
		self.checkmark_opacity = 0.95
		self.animation_length = 650
		
		self.setAlignment(Qt.AlignCenter)
		self.setText("Drag and drop an image here")
		self.setStyleSheet("border: 2px dashed #aaa")
		self.setAcceptDrops(True)
		
		# Status symbol (label)
		self.status_symbol = QLabel(self)
		self.status_symbol.hide()
		self.status_symbol.setFixedSize(64, 64)
		self.status_symbol.setStyleSheet("border: none; z-index: 3000;")
		# Status movie (animated)
		self.status_movie = QtGui.QMovie(r"./_res/check.gif")
		self.status_movie.setScaledSize(self.status_symbol.size())
		self.status_movie.stop()
		self.status_movie.finished.connect(self.end_check)
		self.status_symbol.setMovie(self.status_movie)
		# Status effect (opacity)
		check_opacity_effect = QtWidgets.QGraphicsOpacityEffect(self)
		check_opacity_effect.setOpacity(self.checkmark_opacity)
		self.status_symbol.setGraphicsEffect(check_opacity_effect)
		self.status_symbol.setAutoFillBackground(True)
		
		# Fades
		self.fadein_animation = QtCore.QPropertyAnimation(check_opacity_effect, b"opacity")
		self.fadein_animation.setDuration(self.animation_length)
		self.fadein_animation.setStartValue(0)
		self.fadein_animation.setEndValue(self.checkmark_opacity)
		self.fadein_animation.setEasingCurve(QtCore.QEasingCurve.InQuad)
		
		self.fadeout_animation = QtCore.QPropertyAnimation(check_opacity_effect, b"opacity")
		self.fadeout_animation.setDuration(self.animation_length)
		self.fadeout_animation.setStartValue(self.checkmark_opacity)
		self.fadeout_animation.setEndValue(0)
		self.fadeout_animation.setEasingCurve(QtCore.QEasingCurve.OutQuad)
		self.fadeout_animation.finished.connect(self.stopPlaying)
	
	def start_check(self):
		# Stop animations if already playing
		self.fadein_animation.stop()
		self.fadeout_animation.stop()
		# Stop gif if already playing
		self.status_movie.stop()
		
		# Symbol and fadein start at the same time.
		self.fadein_animation.start()
		self.status_movie.start()
		self.status_symbol.show()
	
	def end_check(self):
		# Triggered by the end of the gif
		self.status_movie.stop()
		self.fadeout_animation.start()
	
	def stopPlaying(self):
		# Triggered by the end of the animation, to ensure the gif is halted / not working needlessly
		self.status_movie.stop()
		self.status_symbol.hide()
	
	def resizeEvent(self, event):
		super().resizeEvent(event)
		self.status_symbol.move(self.width() - self.status_symbol.width(), 0)
	
	def dragEnterEvent(self, event: QDragEnterEvent):
		if event.mimeData().hasUrls():
			event.acceptProposedAction()
	
	def dropEvent(self, event: QDropEvent):
		if not event.mimeData().hasUrls():
			return
		
		event.acceptProposedAction()
		first_url = event.mimeData().urls()[0]  # type: PySide6.QtCore.QUrl
		file_name = first_url.fileName()
		file_ext = file_name.split('.')[-1]
		
		if not QImageReader.supportedImageFormats().__contains__(file_ext):
			return
		
		if first_url.isLocalFile():
			image_path = pathlib.Path(first_url.toLocalFile()).resolve()
			image_qt = PySide6.QtGui.QImage(str(image_path))
			image_pil = Image.open(image_path).convert('RGB')
		else:
			image_data = requests.get(first_url.toString()).content
			image_qt = PySide6.QtGui.QImage.fromData(image_data)
			image_pil = ImageQt.fromqimage(image_qt).convert('RGB')
		
		try:
			decoded_info = artifactual.try_decode_image(image_pil)
			
			if not decoded_info:
				decoded_info = f'No imprinted data found in {file_name}.'
			
			self.imageDropped.emit(decoded_info)
		
		except Exception as e:
			self.imageDropped.emit(f'Error decoding image info: {e}')
		
		self.start_check()
		
		# Scale image to fit the label
		if image_qt.width() > self.width() or image_qt.height() > self.height():
			image_qt = image_qt.scaled(self.width(), self.height(), Qt.KeepAspectRatio)
		
		self.setPixmap(PySide6.QtGui.QPixmap.fromImage(image_qt))

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("ArtiFactual")
		self.setWindowIcon(PySide6.QtGui.QIcon(r"./_res/detective.png"))
		
		central_widget = QWidget(self)
		self.setCentralWidget(central_widget)
		
		layout = QVBoxLayout(central_widget)
		
		# = Image Area
		self.image_area = ImageDropArea()
		self.image_area.setFixedHeight(400)
		self.image_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		# self.image_area.setFixedSize(800, 400)
		layout.addWidget(self.image_area)
		
		# = Text Area
		self.text_area = QTextEdit()
		self.text_area.setPlaceholderText("(Pending)")
		layout.addWidget(self.text_area)
		
		# = Text Area - Highlighter
		self.text_highlighter = QGraphicsColorizeEffect(self)
		self.text_highlighter.setColor(QColor(0, 210, 53, 200))
		self.text_highlighter.setStrength(0.0)
		self.text_area.setGraphicsEffect(self.text_highlighter)
		
		# = Button Bar (Docked to bottom)
		button_bar = QWidget()
		button_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		button_bar_layout = QHBoxLayout(button_bar)
		button_bar_layout.setContentsMargins(0, 0, 0, 0)
		button_bar.setFixedHeight(36)
		layout.addWidget(button_bar)
		
		# = Button Bar - Buttons
		clipboard_button = QPushButton()
		clipboard_button.setIcon(PySide6.QtGui.QIcon(r"./_res/clipboard_i.png"))
		clipboard_button.setText('Copy')
		clipboard_button.setStyleSheet("background-color: #2d2d2d;")
		clipboard_button.clicked.connect(self.copy_to_clipboard)
		clipboard_button.setFixedSize(64, 36)
		clipboard_button.setIconSize(clipboard_button.size() * 0.8)
		button_bar_layout.addWidget(clipboard_button)
		
		exit_button = QPushButton()
		exit_button.setIcon(PySide6.QtGui.QIcon(r"./_res/exit_i.png"))
		exit_button.setText('Exit')
		exit_button.setStyleSheet("background-color: #2d2d2d;")
		exit_button.clicked.connect(self.close)
		exit_button.setFixedSize(64, 36)
		exit_button.setIconSize(exit_button.size() * 0.8)
		button_bar_layout.addWidget(exit_button)
		
		# = Signals
		self.image_area.imageDropped.connect(self.set_text)
	
	def copy_to_clipboard(self):
		clipboard = QApplication.clipboard()
		clipboard.setText(self.text_area.toPlainText())
	
	def set_text(self, some_string):
		self.text_area.clear()
		self.text_area.setPlainText(some_string)

def apply_dark_theme(app):
	dark_palette = QtGui.QPalette()
	dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
	dark_palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
	dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
	dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
	dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
	dark_palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
	dark_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
	dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
	dark_palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
	dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
	dark_palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
	dark_palette.setColor(QtGui.QPalette.PlaceholderText, QtCore.Qt.white)
	dark_palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
	dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, QtCore.Qt.darkGray)
	
	app.setPalette(dark_palette)
	
	app.setStyleSheet(
		"QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }"
	)

def main():
	app = QApplication(sys.argv)
	
	apply_dark_theme(app)
	
	main_window = MainWindow()
	main_window.resize(800, 600)
	main_window.show()
	
	sys.exit(app.exec())

if __name__ == '__main__':
	main()
