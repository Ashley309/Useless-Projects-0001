import sys
import pyautogui
import pygetwindow as gw
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPixmap

# Keywords in browser window titles that trigger tab closure
TARGET_KEYWORDS = ["YouTube", "Stack Overflow", "Reddit", "New Tab"]

class AnnoyingMascot(QWidget):
    def __init__(self):
        super().__init__()
        
        # Transparent, frameless, always-on-top window setup
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Load avatar images
        self.idle_pixmap = QPixmap("idle.png")
        self.cute_pixmap = QPixmap("cute.png")
        
        self.label = QLabel(self)
        self.label.setPixmap(self.idle_pixmap)
        self.resize(self.idle_pixmap.width(), self.idle_pixmap.height())
        
        # Calculate screen center coordinates
        self.screen_geo = QApplication.desktop().availableGeometry()
        self.center_x = (self.screen_geo.width() - self.width()) // 2
        self.center_y = (self.screen_geo.height() - self.height()) // 2
        
        # Default position: Exact center of screen
        self.move(self.center_x, self.center_y)
        
        # Smooth gliding animation setup
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(350)  # Glide duration in ms
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        
        self.is_attacking = False
        self.is_paused = False  # Track paused state

        # Check active window every 400ms
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.scan_and_close_tab)
        self.check_timer.start(400)

    def scan_and_close_tab(self):
        # Skip scanning if already attacking or if paused
        if self.is_attacking or self.is_paused:
            return

        try:
            active_win = gw.getActiveWindow()
            if active_win and active_win.title:
                for keyword in TARGET_KEYWORDS:
                    if keyword.lower() in active_win.title.lower():
                        self.is_attacking = True
                        
                        # Target position: Active tab's close button area
                        target_x = active_win.left + active_win.width - 60 - (self.width() // 2)
                        target_y = active_win.top + 35 - (self.height() // 2)
                        
                        # Keep inside screen boundaries
                        target_x = max(0, min(target_x, self.screen_geo.width() - self.width()))
                        target_y = max(0, min(target_y, self.screen_geo.height() - self.height()))
                        
                        self.execute_attack(target_x, target_y)
                        break
        except Exception:
            self.is_attacking = False

    def execute_attack(self, target_x, target_y):
        # 1. Glide avatar center to tab close button
        self.anim.stop()
        self.anim.setStartValue(self.pos())
        self.anim.setEndValue(QPoint(target_x, target_y))
        
        def on_reach_target():
            self.anim.finished.disconnect(on_reach_target)
            
            # Close active tab
            pyautogui.hotkey('ctrl', 'w')
            
            # Show cute face reaction
            self.label.setPixmap(self.cute_pixmap)
            
            # Hover over close button position for exactly 0.5 seconds (500ms), then return to center
            QTimer.singleShot(500, self.return_to_center)

        self.anim.finished.connect(on_reach_target)
        self.anim.start()

    def return_to_center(self):
        # Reset image back to idle graphic
        self.label.setPixmap(self.idle_pixmap)
        
        # 2. Glide avatar back to screen center
        self.anim.stop()
        self.anim.setStartValue(self.pos())
        self.anim.setEndValue(QPoint(self.center_x, self.center_y))
        
        def on_returned():
            self.anim.finished.disconnect(on_returned)
            self.is_attacking = False

        self.anim.finished.connect(on_returned)
        self.anim.start()

    # Mouse interactions: Left-click drags, Right-click pauses/resumes mascot
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
        elif event.button() == Qt.RightButton:
            self.is_paused = not self.is_paused
            # If pausing mid-animation, stop active movement
            if self.is_paused:
                self.anim.stop()
                self.is_attacking = False

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mascot = AnnoyingMascot()
    mascot.show()
    sys.exit(app.exec_())