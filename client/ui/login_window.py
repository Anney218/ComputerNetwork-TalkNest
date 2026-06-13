import os
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QTimer, QRectF
from PySide6.QtGui import QPixmap, QLinearGradient, QPalette, QBrush, QColor, QFont, QFontDatabase, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QFrame, QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy
)

from client.controllers.login_controller import LoginController


class LoginWindow(QWidget):
    def __init__(self, network_client):
        super().__init__()
        self.network_client = network_client
        self.controller = LoginController(self, network_client)
        self.drag_position = None

        self.setWindowTitle("TalkNest - Login")
        self.resize(1280, 800)
        self.setMinimumSize(1100, 700)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.build_ui()
        self.apply_shadows()
        self.animate_entry()

    def animate_entry(self):
        self.setWindowOpacity(0)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(800)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()
        
        # Scale animation for main container
        self.scale_anim = QPropertyAnimation(self.main_container, b"geometry")
        self.scale_anim.setDuration(800)
        self.scale_anim.setEasingCurve(QEasingCurve.Type.OutBack)
        start_geo = self.main_container.geometry()
        start_geo = start_geo.adjusted(60, 40, -60, -40)
        self.scale_anim.setStartValue(start_geo)
        self.scale_anim.setEndValue(self.main_container.geometry())
        self.scale_anim.start()

    def apply_shadows(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(80)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 30)
        self.main_container.setGraphicsEffect(shadow)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.drag_position:
            delta = event.globalPosition().toPoint() - self.drag_position
            self.move(self.pos() + delta)
            self.drag_position = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.drag_position = None

    def build_ui(self):
        # Main layout with center alignment
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setAlignment(Qt.AlignCenter)

        # Main container - centered card with premium glass effect
        self.main_container = QFrame()
        self.main_container.setObjectName("mainContainer")
        self.main_container.setFixedSize(560, 720)
        self.main_container.setStyleSheet("""
            QFrame#mainContainer {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(20, 24, 35, 0.98),
                    stop:0.5 rgba(15, 18, 28, 0.98),
                    stop:1 rgba(10, 13, 23, 0.98));
                border-radius: 56px;
                border: 1px solid rgba(255,255,255,0.12);
            }
        """)

        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(50, 40, 50, 40)
        container_layout.setSpacing(18)

        # ========== WINDOW CONTROLS ==========
        controls = QHBoxLayout()
        controls.setSpacing(12)

        minimize_btn = QPushButton("─")
        minimize_btn.setFixedSize(32, 32)
        minimize_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.08);
                color: white;
                border-radius: 16px;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.18);
            }
        """)
        minimize_btn.clicked.connect(self.showMinimized)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(32, 32)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.08);
                color: white;
                border-radius: 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #EF4444;
            }
        """)
        close_btn.clicked.connect(self.close)

        controls.addWidget(minimize_btn)
        controls.addWidget(close_btn)
        controls.addStretch()

        container_layout.addLayout(controls)

        # ========== PREMIUM LOGO SECTION ==========
        logo_container = QFrame()
        logo_container.setFixedSize(120, 120)
        logo_container.setStyleSheet("""
            QFrame {
                background: qconicalgradient(cx:0.5, cy:0.5, angle:0,
                    stop:0 #F59E0B, 
                    stop:0.25 #EC4899, 
                    stop:0.5 #8B5CF6, 
                    stop:0.75 #06B6D4, 
                    stop:1 #10B981);
                border-radius: 60px;
                border: 2px solid rgba(255,255,255,0.2);
            }
        """)
        
        logo_shadow = QGraphicsDropShadowEffect()
        logo_shadow.setBlurRadius(50)
        logo_shadow.setColor(QColor(139, 92, 246, 150))
        logo_shadow.setOffset(0, 8)
        logo_container.setGraphicsEffect(logo_shadow)
        
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setAlignment(Qt.AlignCenter)
        
        # New logo - Bird/Talk bubble icon
        logo_icon = QLabel("💬")
        logo_icon.setStyleSheet("font-size: 56px; background: transparent;")
        logo_icon.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo_icon)

        container_layout.addWidget(logo_container, alignment=Qt.AlignCenter)

        # ========== BRAND TITLE ==========
        title = QLabel("TalkNest")
        title.setStyleSheet("""
            QLabel {
                font-size: 48px;
                font-weight: 900;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFFFFF, 
                    stop:0.3 #A78BFA, 
                    stop:0.7 #F472B6, 
                    stop:1 #60A5FA);
                letter-spacing: 3px;
                margin-top: 10px;
            }
        """)
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Where Conversations Come Alive ✨")
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(255,255,255,0.6);
                font-size: 13px;
                font-weight: 500;
                letter-spacing: 1.5px;
                background: transparent;
            }
        """)
        subtitle.setAlignment(Qt.AlignCenter)

        container_layout.addWidget(title)
        container_layout.addWidget(subtitle)

        container_layout.addSpacing(15)

        # ========== FEATURE BADGES (Enhanced) ==========
        badges_layout = QHBoxLayout()
        badges_layout.setSpacing(10)

        badges = [
            ("🚀", "Lightning Fast"),
            ("🔒", "Secure Chat"),
            ("💬", "Real-time"),
            ("🎨", "Beautiful UI")
        ]

        for icon, text in badges:
            badge = QFrame()
            badge.setStyleSheet("""
                QFrame {
                    background: rgba(255,255,255,0.07);
                    border-radius: 22px;
                    border: 1px solid rgba(255,255,255,0.08);
                }
                QFrame:hover {
                    background: rgba(139, 92, 246, 0.15);
                    border-color: rgba(139, 92, 246, 0.3);
                }
            """)
            badge_layout = QHBoxLayout(badge)
            badge_layout.setContentsMargins(14, 8, 14, 8)
            badge_layout.setSpacing(8)
            
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 13px; background: transparent;")
            text_lbl = QLabel(text)
            text_lbl.setStyleSheet("color: rgba(255,255,255,0.75); font-size: 11px; font-weight: 600; background: transparent;")
            
            badge_layout.addWidget(icon_lbl)
            badge_layout.addWidget(text_lbl)
            
            badges_layout.addWidget(badge)

        container_layout.addLayout(badges_layout)

        container_layout.addSpacing(25)

        # ========== LOGIN FORM ==========
        # Username Field with icon
        user_container = QFrame()
        user_container.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.06);
                border: 1.5px solid rgba(255,255,255,0.1);
                border-radius: 30px;
            }
            QFrame:focus-within {
                border-color: #8B5CF6;
                background: rgba(139, 92, 246, 0.1);
            }
        """)
        user_container.setFixedHeight(60)

        user_layout = QHBoxLayout(user_container)
        user_layout.setContentsMargins(22, 0, 22, 0)

        user_icon = QLabel("👤")
        user_icon.setStyleSheet("font-size: 20px; background: transparent;")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                font-size: 14px;
                color: white;
                padding: 14px 0;
                font-weight: 500;
            }
            QLineEdit:focus {
                outline: none;
            }
            QLineEdit::placeholder {
                color: rgba(255,255,255,0.4);
                font-weight: 400;
            }
        """)

        user_layout.addWidget(user_icon)
        user_layout.addWidget(self.username_input)

        container_layout.addWidget(user_container)

        # Error Label with glass effect
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("""
            QLabel {
                color: #F87171;
                font-size: 12px;
                padding: 10px 16px;
                background: rgba(248, 113, 113, 0.12);
                border-radius: 16px;
                border-left: 3px solid #F87171;
            }
        """)
        self.error_label.setWordWrap(True)
        self.error_label.hide()

        container_layout.addWidget(self.error_label)

        # Premium Login Button with gradient animation
        self.login_button = QPushButton("Start Talking →")
        self.login_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8B5CF6,
                    stop:0.5 #EC4899,
                    stop:1 #06B6D4);
                color: white;
                border: none;
                border-radius: 30px;
                padding: 16px;
                font-size: 16px;
                font-weight: 800;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7C3AED,
                    stop:0.5 #DB2777,
                    stop:1 #0891B2);
            }
            QPushButton:pressed {
                padding-top: 17px;
                padding-bottom: 15px;
            }
        """)
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.clicked.connect(self.on_login_clicked)

        container_layout.addWidget(self.login_button)

        # Elegant Divider
        divider_layout = QHBoxLayout()
        line_left = QFrame()
        line_left.setFrameShape(QFrame.HLine)
        line_left.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 transparent, stop:0.5 rgba(255,255,255,0.1), stop:1 transparent); max-height: 1px;")
        or_label = QLabel("try instantly")
        or_label.setStyleSheet("color: rgba(255,255,255,0.45); padding: 0 18px; font-size: 10px; font-weight: 700; letter-spacing: 1.5px; background: transparent;")
        line_right = QFrame()
        line_right.setFrameShape(QFrame.HLine)
        line_right.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 transparent, stop:0.5 rgba(255,255,255,0.1), stop:1 transparent); max-height: 1px;")

        divider_layout.addWidget(line_left, 1)
        divider_layout.addWidget(or_label)
        divider_layout.addWidget(line_right, 1)

        container_layout.addLayout(divider_layout)

        # Demo Quick Access with better design
        demo_label = QLabel("⚡ QUICK DEMO ACCESS ⚡")
        demo_label.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 10px; font-weight: 700; letter-spacing: 2px; background: transparent;")
        demo_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(demo_label)

        demo_grid = QVBoxLayout()
        demo_grid.setSpacing(10)

        demo_accounts = [
            ("🌟 Guest Explorer", "guest", "Try as guest"),
            ("👑 Admin Hub", "admin", "Full access demo"),
            ("💎 Premium Member", "pro_demo", "Pro features"),
            ("🎨 Creative Studio", "designer", "Designer mode")
        ]

        for btn_text, username, tooltip in demo_accounts:
            demo_btn = QPushButton(f"{btn_text}")
            demo_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,0.05);
                    color: rgba(255,255,255,0.85);
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 22px;
                    padding: 12px;
                    font-size: 13px;
                    font-weight: 600;
                    text-align: left;
                    padding-left: 22px;
                }
                QPushButton:hover {
                    background: rgba(139, 92, 246, 0.2);
                    border-color: #8B5CF6;
                    color: white;
                    padding-left: 28px;
                }
            """)
            demo_btn.setCursor(Qt.PointingHandCursor)
            demo_btn.setToolTip(tooltip)
            demo_btn.clicked.connect(lambda checked, u=username: self.username_input.setText(u))
            demo_grid.addWidget(demo_btn)

        container_layout.addLayout(demo_grid)

        container_layout.addStretch()

        # ========== FOOTER with animated text ==========
        footer = QLabel("🐦 Join the flock • End-to-end encrypted • 100% Free 🐦")
        footer.setStyleSheet("""
            QLabel {
                color: rgba(255,255,255,0.3);
                font-size: 10px;
                font-weight: 600;
                letter-spacing: 1px;
                background: transparent;
            }
        """)
        footer.setAlignment(Qt.AlignCenter)

        container_layout.addWidget(footer)

        main_layout.addWidget(self.main_container, alignment=Qt.AlignCenter)

        # Add floating particles for visual magic
        self.setup_magic_particles()

    def setup_magic_particles(self):
        """Setup floating background particles for magical effect"""
        self.particles = []
        
        particle_colors = [
            "#8B5CF6", "#EC4899", "#06B6D4", "#F59E0B", "#10B981"
        ]
        
        positions = [
            (80, 150), (1150, 200), (120, 600), (1120, 550),
            (40, 400), (1200, 400), (550, 80), (680, 700),
            (350, 90), (900, 720), (200, 350), (1050, 300)
        ]
        
        for i, (x, y) in enumerate(positions):
            particle = QLabel(self)
            particle.setFixedSize(6, 6)
            color = particle_colors[i % len(particle_colors)]
            particle.setStyleSheet(f"""
                QLabel {{
                    background: {color};
                    border-radius: 3px;
                    opacity: 0.4;
                }}
            """)
            particle.move(x, y)
            particle.show()
            
            # Floating animation
            anim = QPropertyAnimation(particle, b"pos")
            anim.setDuration(4000 + (i * 400))
            anim.setEasingCurve(QEasingCurve.Type.InOutSine)
            
            # Random movement
            move_x = 30 if i % 2 == 0 else -30
            move_y = 40 if i % 3 == 0 else -20
            
            anim.setStartValue(particle.pos())
            anim.setEndValue(QPoint(x + move_x, y + move_y))
            anim.setLoopCount(-1)
            anim.start()
            
            # Fade animation
            fade = QPropertyAnimation(particle, b"windowOpacity")
            fade.setDuration(3000 + (i * 300))
            fade.setEasingCurve(QEasingCurve.Type.InOutSine)
            fade.setStartValue(0.2)
            fade.setEndValue(0.6)
            fade.setLoopCount(-1)
            fade.start()
            
            self.particles.append((particle, anim, fade))

    def on_login_clicked(self):
        username = self.username_input.text().strip()
        if not username:
            self.show_error("Please enter your username")
            return

        self.error_label.hide()
        self.login_button.setText("🔄 Connecting to TalkNest...")
        self.login_button.setEnabled(False)

        self.controller.login(username)

    def show_error(self, message):
        self.error_label.setText("⚠️ " + message)
        self.error_label.show()
        
        # Premium shake animation
        shake = QPropertyAnimation(self.error_label, b"pos")
        shake.setDuration(350)
        shake.setEasingCurve(QEasingCurve.Type.InOutQuad)
        original_pos = self.error_label.pos()
        
        for i in range(4):
            offset = 10 if i % 2 == 0 else -10
            shake.setKeyValueAt(i/4, original_pos + QPoint(offset, 0))
        
        shake.setEndValue(original_pos)
        shake.start()
        
        self.login_button.setText("Start Talking →")
        self.login_button.setEnabled(True)