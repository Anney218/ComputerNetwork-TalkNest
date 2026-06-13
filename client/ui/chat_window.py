import os
from datetime import datetime

from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QTimer
from PySide6.QtGui import QFont, QColor, QIcon, QLinearGradient, QBrush
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QTextEdit, QFrame, QScrollArea,
    QMessageBox, QGraphicsDropShadowEffect, QLineEdit, QStackedWidget
)

from client.controllers.chat_controller import ChatController
from client.ui.widgets.user_list_item import UserListItem


class ChatWindow(QWidget):
    def __init__(self, network_client, username, initial_room="General"):
        super().__init__()
        self.network_client = network_client
        self.username = username
        self.current_room = initial_room
        self.target_mode = "public"
        self.target_name = None
        self.drag_position = None
        self.all_users = []
        self.is_maximized = False

        self.controller = ChatController(self, network_client)

        self.setWindowTitle(f"TalkNest - {username}")
        self.resize(1400, 900)
        self.setMinimumSize(1200, 780)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.build_ui()
        self.connect_signals()
        self.animate_entry()

    def animate_entry(self):
        self.setWindowOpacity(0)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(600)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

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
        # Main container with premium gradient
        main_container = QFrame(self)
        main_container.setObjectName("mainContainer")
        main_container.setStyleSheet("""
            QFrame#mainContainer {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0F172A,
                    stop:0.5 #1E1B4B,
                    stop:1 #0F172A);
                border-radius: 28px;
                border: 1px solid rgba(139, 92, 246, 0.3);
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setColor(QColor(139, 92, 246, 80))
        shadow.setOffset(0, 15)
        main_container.setGraphicsEffect(shadow)

        container_layout = QVBoxLayout(main_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # ========== TOP BAR ==========
        top_bar = QFrame()
        top_bar.setFixedHeight(75)
        top_bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(30, 27, 75, 0.95),
                    stop:1 rgba(15, 23, 42, 0.95));
                border-top-left-radius: 28px;
                border-top-right-radius: 28px;
                border-bottom: 1px solid rgba(139, 92, 246, 0.3);
            }
        """)
        
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(28, 0, 28, 0)
        
        # Logo Section
        logo_wrapper = QHBoxLayout()
        logo_wrapper.setSpacing(12)
        
        logo_bg = QFrame()
        logo_bg.setFixedSize(40, 40)
        logo_bg.setStyleSheet("""
            QFrame {
                background: qconicalgradient(cx:0.5, cy:0.5, angle:0,
                    stop:0 #8B5CF6,
                    stop:0.5 #EC4899,
                    stop:1 #06B6D4);
                border-radius: 20px;
            }
        """)
        logo_bg_layout = QVBoxLayout(logo_bg)
        logo_bg_layout.setAlignment(Qt.AlignCenter)
        logo_icon = QLabel("🐦")
        logo_icon.setStyleSheet("font-size: 22px; background: transparent;")
        logo_bg_layout.addWidget(logo_icon)
        
        logo_text = QLabel("TalkNest")
        logo_text.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #A78BFA,
                    stop:1 #F472B6);
                font-size: 22px;
                font-weight: 800;
                letter-spacing: 1.5px;
            }
        """)
        
        logo_wrapper.addWidget(logo_bg)
        logo_wrapper.addWidget(logo_text)
        
        # Mode Selector
        mode_selector = QFrame()
        mode_selector.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.05);
                border-radius: 35px;
                border: 1px solid rgba(139, 92, 246, 0.4);
                padding: 4px;
            }
        """)
        mode_layout = QHBoxLayout(mode_selector)
        mode_layout.setContentsMargins(4, 4, 4, 4)
        mode_layout.setSpacing(8)
        
        self.public_btn = QPushButton("🌍 Global")
        self.public_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8B5CF6,
                    stop:1 #6D28D9);
                color: white;
                border: none;
                border-radius: 28px;
                padding: 10px 28px;
                font-size: 13px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7C3AED,
                    stop:1 #5B21B6);
            }
        """)
        self.public_btn.clicked.connect(self.activate_public_mode)
        
        self.private_btn = QPushButton("💬 Private")
        self.private_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: rgba(255,255,255,0.8);
                border: none;
                border-radius: 28px;
                padding: 10px 28px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.1);
                color: white;
            }
        """)
        self.private_btn.clicked.connect(self.show_private_section)
        
        mode_layout.addWidget(self.public_btn)
        mode_layout.addWidget(self.private_btn)
        
        # Search Users
        self.search_container = QFrame()
        self.search_container.setVisible(False)
        self.search_container.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.05);
                border-radius: 28px;
                border: 1px solid rgba(139, 92, 246, 0.4);
                padding: 4px;
            }
        """)
        search_layout = QHBoxLayout(self.search_container)
        search_layout.setContentsMargins(16, 4, 16, 4)
        
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 14px; color: #A78BFA;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search users...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: white;
                font-size: 13px;
                padding: 8px 0;
            }
            QLineEdit::placeholder {
                color: rgba(255,255,255,0.5);
            }
        """)
        self.search_input.textChanged.connect(self.filter_users)
        
        self.online_badge = QLabel("0 online")
        self.online_badge.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #10B981,
                    stop:1 #059669);
                color: white;
                font-size: 11px;
                font-weight: 700;
                padding: 5px 14px;
                border-radius: 18px;
            }
        """)
        
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(self.online_badge)
        
        # User Profile
        profile_wrapper = QFrame()
        profile_wrapper.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.08);
                border: 1px solid rgba(139, 92, 246, 0.4);
                border-radius: 35px;
            }
        """)
        profile_layout = QHBoxLayout(profile_wrapper)
        profile_layout.setContentsMargins(14, 6, 18, 6)
        profile_layout.setSpacing(10)
        
        avatar_bg = QFrame()
        avatar_bg.setFixedSize(34, 34)
        avatar_bg.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #8B5CF6,
                    stop:1 #EC4899);
                border-radius: 17px;
            }
        """)
        avatar_layout = QVBoxLayout(avatar_bg)
        avatar_layout.setAlignment(Qt.AlignCenter)
        avatar = QLabel("👤")
        avatar.setStyleSheet("font-size: 18px; background: transparent;")
        avatar_layout.addWidget(avatar)
        
        username_label = QLabel(self.username)
        username_label.setStyleSheet("color: white; font-size: 13px; font-weight: 600;")
        
        status_dot = QFrame()
        status_dot.setFixedSize(10, 10)
        status_dot.setStyleSheet("""
            QFrame {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    stop:0 #10B981,
                    stop:1 #059669);
                border-radius: 5px;
            }
        """)
        
        profile_layout.addWidget(avatar_bg)
        profile_layout.addWidget(username_label)
        profile_layout.addWidget(status_dot)
        
        # Window Controls
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(10)
        
        min_btn = self.create_control_btn("─")
        min_btn.clicked.connect(self.showMinimized)
        
        max_btn = self.create_control_btn("□")
        max_btn.clicked.connect(self.toggle_maximize)
        
        close_btn = self.create_control_btn("✕")
        close_btn.clicked.connect(self.close)
        
        ctrl_layout.addWidget(min_btn)
        ctrl_layout.addWidget(max_btn)
        ctrl_layout.addWidget(close_btn)
        
        top_layout.addLayout(logo_wrapper)
        top_layout.addStretch()
        top_layout.addWidget(mode_selector)
        top_layout.addSpacing(20)
        top_layout.addWidget(self.search_container)
        top_layout.addSpacing(20)
        top_layout.addWidget(profile_wrapper)
        top_layout.addSpacing(15)
        top_layout.addLayout(ctrl_layout)
        
        # ========== MAIN CONTENT ==========
        content_area = QHBoxLayout()
        content_area.setContentsMargins(0, 0, 0, 0)
        content_area.setSpacing(0)
        
        # ========== LEFT SIDEBAR ==========
        self.user_sidebar = QFrame()
        self.user_sidebar.setFixedWidth(360)
        self.user_sidebar.setStyleSheet("""
            QFrame {
                background: rgba(15, 23, 42, 0.9);
                border-right: 1px solid rgba(139, 92, 246, 0.3);
            }
        """)
        
        sidebar_layout = QVBoxLayout(self.user_sidebar)
        sidebar_layout.setContentsMargins(20, 25, 20, 25)
        sidebar_layout.setSpacing(18)
        
        sidebar_header = QLabel("✦ ACTIVE USERS ✦")
        sidebar_header.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #A78BFA,
                    stop:1 #F472B6);
                font-size: 12px;
                font-weight: 800;
                letter-spacing: 1.5px;
                padding: 8px;
            }
        """)
        sidebar_header.setAlignment(Qt.AlignCenter)
        
        self.user_list = QListWidget()
        self.user_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                padding: 0px;
                margin: 4px 0;
            }
        """)
        self.user_list.itemClicked.connect(self.select_private_user)
        
        sidebar_layout.addWidget(sidebar_header)
        sidebar_layout.addWidget(self.user_list, 1)
        
        # Admin buttons
        if self.username.lower() == "admin":
            admin_frame = QFrame()
            admin_frame.setStyleSheet("""
                QFrame {
                    background: rgba(239, 68, 68, 0.15);
                    border-radius: 20px;
                    border: 1px solid rgba(239, 68, 68, 0.4);
                    margin-top: 10px;
                }
            """)
            admin_layout = QHBoxLayout(admin_frame)
            admin_layout.setContentsMargins(16, 12, 16, 12)
            admin_layout.setSpacing(12)
            
            self.kick_btn = QPushButton("🚫 Kick")
            self.kick_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #EF4444,
                        stop:1 #DC2626);
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 8px;
                    font-size: 12px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #DC2626,
                        stop:1 #B91C1C);
                }
            """)
            self.kick_btn.clicked.connect(self.kick_selected_user)
            
            self.ban_btn = QPushButton("⛔ Ban")
            self.ban_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #F59E0B,
                        stop:1 #D97706);
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 8px;
                    font-size: 12px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #D97706,
                        stop:1 #B45309);
                }
            """)
            self.ban_btn.clicked.connect(self.ban_selected_user)
            
            admin_layout.addWidget(self.kick_btn)
            admin_layout.addWidget(self.ban_btn)
            sidebar_layout.addWidget(admin_frame)
        
        # ========== RIGHT CHAT AREA ==========
        chat_area = QFrame()
        chat_area.setStyleSheet("background: rgba(15, 23, 42, 0.6);")
        
        chat_layout = QVBoxLayout(chat_area)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)
        
        # Chat Header
        chat_header = QFrame()
        chat_header.setFixedHeight(70)
        chat_header.setStyleSheet("""
            QFrame {
                background: rgba(30, 27, 75, 0.5);
                border-bottom: 1px solid rgba(139, 92, 246, 0.2);
            }
        """)
        header_layout = QHBoxLayout(chat_header)
        header_layout.setContentsMargins(35, 0, 35, 0)
        
        header_info = QVBoxLayout()
        header_info.setSpacing(5)
        
        self.chat_title = QLabel("🌍 Global Chat")
        self.chat_title.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #A78BFA,
                    stop:1 #F472B6);
                font-size: 20px;
                font-weight: 800;
            }
        """)
        
        self.chat_subtitle = QLabel("✨ Everyone in the channel")
        self.chat_subtitle.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 12px;")
        
        header_info.addWidget(self.chat_title)
        header_info.addWidget(self.chat_subtitle)
        
        header_layout.addLayout(header_info)
        
        # Messages Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(255,255,255,0.05);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8B5CF6,
                    stop:1 #EC4899);
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7C3AED,
                    stop:1 #DB2777);
            }
        """)
        
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(35, 30, 35, 30)
        self.messages_layout.setSpacing(15)
        self.messages_layout.addStretch()
        
        self.scroll.setWidget(self.messages_container)
        
        # Input Area
        input_container = QFrame()
        input_container.setFixedHeight(110)
        input_container.setStyleSheet("""
            QFrame {
                background: rgba(30, 27, 75, 0.5);
                border-top: 1px solid rgba(139, 92, 246, 0.2);
                border-bottom-left-radius: 28px;
                border-bottom-right-radius: 28px;
            }
        """)
        
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(35, 15, 35, 15)
        input_layout.setSpacing(10)
        
        self.context_label = QLabel("📝 Sending to: Global Chat")
        self.context_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #A78BFA,
                    stop:1 #F472B6);
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.5px;
                padding: 0 5px;
            }
        """)
        
        input_row = QHBoxLayout()
        input_row.setSpacing(15)
        
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Type your message...")
        self.message_input.setStyleSheet("""
            QTextEdit {
                background: rgba(255,255,255,0.08);
                border: 1px solid rgba(139, 92, 246, 0.3);
                border-radius: 24px;
                padding: 14px 20px;
                font-size: 13px;
                color: white;
            }
            QTextEdit:focus {
                border-color: #8B5CF6;
                background: rgba(139, 92, 246, 0.15);
            }
            QTextEdit::placeholder {
                color: rgba(255,255,255,0.4);
            }
        """)
        self.message_input.setFixedHeight(60)
        self.message_input.installEventFilter(self)
        
        self.send_btn = QPushButton("Send →")
        self.send_btn.setFixedSize(90, 60)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8B5CF6,
                    stop:1 #6D28D9);
                color: white;
                border: none;
                border-radius: 24px;
                font-size: 14px;
                font-weight: 800;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7C3AED,
                    stop:1 #5B21B6);
            }
        """)
        self.send_btn.clicked.connect(self.send_message)
        
        input_row.addWidget(self.message_input, 1)
        input_row.addWidget(self.send_btn)
        
        input_layout.addWidget(self.context_label)
        input_layout.addLayout(input_row)
        
        # Assemble chat
        chat_layout.addWidget(chat_header)
        chat_layout.addWidget(self.scroll, 1)
        chat_layout.addWidget(input_container)
        
        # Assemble main content
        content_area.addWidget(self.user_sidebar)
        content_area.addWidget(chat_area, 1)
        
        container_layout.addWidget(top_bar)
        container_layout.addLayout(content_area, 1)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addWidget(main_container)
        
        # Welcome messages
        self.add_system_notice(f"✨ Welcome to TalkNest, {self.username}! ✨")
        self.add_system_notice("💡 Click 'Private' to see online users and start private chats")
    
    def create_control_btn(self, text):
        btn = QPushButton(text)
        btn.setFixedSize(34, 34)
        btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.08);
                color: white;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(139, 92, 246, 0.5);
            }
        """)
        return btn
    
    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self.is_maximized = False
        else:
            self.showMaximized()
            self.is_maximized = True
    
    def show_private_section(self):
        """Show private chat mode with user list"""
        self.private_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8B5CF6,
                    stop:1 #6D28D9);
                color: white;
                border: none;
                border-radius: 28px;
                padding: 10px 28px;
                font-size: 13px;
                font-weight: 700;
            }
        """)
        self.public_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: rgba(255,255,255,0.8);
                border: none;
                border-radius: 28px;
                padding: 10px 28px;
                font-size: 13px;
                font-weight: 600;
            }
        """)
        
        self.user_sidebar.setVisible(True)
        self.search_container.setVisible(True)
        
        if not self.target_name or self.target_mode != "private":
            self.chat_title.setText("💬 Select a User")
            self.chat_subtitle.setText("✨ Click on any user to start chatting")
            self.context_label.setText("💬 Select a user from the left panel")
    
    def activate_public_mode(self):
        self.target_mode = "public"
        self.target_name = None
        
        self.public_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8B5CF6,
                    stop:1 #6D28D9);
                color: white;
                border: none;
                border-radius: 28px;
                padding: 10px 28px;
                font-size: 13px;
                font-weight: 700;
            }
        """)
        self.private_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: rgba(255,255,255,0.8);
                border: none;
                border-radius: 28px;
                padding: 10px 28px;
                font-size: 13px;
                font-weight: 600;
            }
        """)
        
        self.user_sidebar.setVisible(False)
        self.search_container.setVisible(False)
        
        self.chat_title.setText("🌍 Global Chat")
        self.chat_subtitle.setText("✨ Everyone in the channel")
        self.context_label.setText("📝 Sending to: Global Chat")

    def eventFilter(self, obj, event):
        if obj == self.message_input and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key_Return and not event.modifiers() & Qt.ShiftModifier:
                self.send_message()
                return True
        return super().eventFilter(obj, event)
    
    def filter_users(self, text):
        for i in range(self.user_list.count()):
            item = self.user_list.item(i)
            username = item.data(Qt.UserRole)
            if username and text.lower() in username.lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def connect_signals(self):
        self.network_client.public_message_received.connect(self.on_public_message)
        self.network_client.private_message_received.connect(self.on_private_message)
        self.network_client.join_notice_received.connect(self.on_notice)
        self.network_client.leave_notice_received.connect(self.on_notice)
        self.network_client.user_list_received.connect(self.update_user_list)
        self.network_client.error_received.connect(self.show_error)
        self.network_client.admin_response_received.connect(self.show_info)
        self.network_client.disconnected.connect(self.on_disconnected)

    def current_time(self):
        return datetime.now().strftime("%I:%M %p")

    def add_message_bubble(self, sender, message, own=False):
        # Create message bubble
        bubble_widget = QFrame()
        bubble_widget.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.08);
                border-radius: 20px;
                margin: 2px 0;
                border: 1px solid rgba(139, 92, 246, 0.3);
            }
        """)
        
        bubble_layout = QVBoxLayout(bubble_widget)
        bubble_layout.setContentsMargins(16, 12, 16, 12)
        bubble_layout.setSpacing(6)
        
        # Sender name
        sender_label = QLabel(sender)
        sender_label.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #A78BFA,
                    stop:1 #F472B6);
                font-size: 11px;
                font-weight: 800;
                letter-spacing: 0.5px;
            }}
        """)
        
        # Message content
        message_label = QLabel(message)
        message_label.setStyleSheet("""
            QLabel {
                color: rgba(255,255,255,0.9);
                font-size: 13px;
                font-weight: 500;
                word-wrap: break-word;
            }
        """)
        message_label.setWordWrap(True)
        message_label.setMaximumWidth(500)
        
        # Time
        time_label = QLabel(self.current_time())
        time_label.setStyleSheet("""
            QLabel {
                color: rgba(255,255,255,0.4);
                font-size: 9px;
            }
        """)
        
        bubble_layout.addWidget(sender_label)
        bubble_layout.addWidget(message_label)
        
        time_layout = QHBoxLayout()
        time_layout.addStretch()
        time_layout.addWidget(time_label)
        bubble_layout.addLayout(time_layout)
        
        if own:
            # Own message - right aligned
            bubble_widget.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 rgba(139, 92, 246, 0.4),
                        stop:1 rgba(236, 73, 153, 0.4));
                    border-radius: 20px;
                    margin: 2px 0;
                    border: 1px solid rgba(139, 92, 246, 0.6);
                }
            """)
            sender_label.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #C7D2FE,
                        stop:1 #F9A8D4);
                    font-size: 11px;
                    font-weight: 800;
                }
            """)
            message_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 13px;
                    font-weight: 500;
                }
            """)
            time_label.setStyleSheet("""
                QLabel {
                    color: rgba(255,255,255,0.5);
                    font-size: 9px;
                }
            """)
            
            container_widget = QWidget()
            container_layout = QHBoxLayout(container_widget)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.addStretch()
            container_layout.addWidget(bubble_widget)
            
            self.messages_layout.insertWidget(self.messages_layout.count() - 1, container_widget)
        else:
            # Left align for others' messages
            container_widget = QWidget()
            container_layout = QHBoxLayout(container_widget)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.addWidget(bubble_widget)
            container_layout.addStretch()
            
            self.messages_layout.insertWidget(self.messages_layout.count() - 1, container_widget)
        
        QTimer.singleShot(50, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        ))

    def add_system_notice(self, text):
        notice = QLabel(text)
        notice.setStyleSheet("""
            QLabel {
                background: rgba(139, 92, 246, 0.15);
                color: #A78BFA;
                font-size: 12px;
                font-weight: 600;
                padding: 12px 24px;
                border-radius: 28px;
                margin: 8px 0;
                border: 1px solid rgba(139, 92, 246, 0.3);
            }
        """)
        notice.setAlignment(Qt.AlignCenter)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, notice)
        
        QTimer.singleShot(50, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        ))

    def select_private_user(self, item):
        selected = item.data(Qt.UserRole)
        if not selected or selected == self.username:
            return

        self.target_mode = "private"
        self.target_name = selected
        self.chat_title.setText(f"💬 {selected}")
        self.chat_subtitle.setText("✨ Direct message")
        self.context_label.setText(f"🔒 Sending to: {selected}")
        
        self.user_list.clearSelection()

    def send_message(self):
        msg = self.message_input.toPlainText().strip()
        if not msg:
            return

        self.controller.send_message(self.target_mode, self.target_name, msg)

        if self.target_mode == "public":
            self.add_message_bubble("You", msg, own=True)
        elif self.target_mode == "private" and self.target_name:
            self.add_message_bubble(f"You → {self.target_name}", msg, own=True)

        self.message_input.clear()

    def on_public_message(self, packet):
        sender = packet.get("sender", "Unknown")
        if sender == self.username:
            return
        self.add_message_bubble(sender, packet.get("message", ""), own=False)

    def on_private_message(self, packet):
        sender = packet.get("sender", "Unknown")
        target = packet.get("target", "")
        
        if target == self.username:
            if self.target_mode != "private" or self.target_name != sender:
                self.target_mode = "private"
                self.target_name = sender
                self.chat_title.setText(f"💬 {sender}")
                self.chat_subtitle.setText("✨ Direct message")
                self.context_label.setText(f"🔒 Sending to: {sender}")
            
            self.add_message_bubble(f"{sender}", packet.get("message", ""), own=False)

    def on_notice(self, msg):
        self.add_system_notice(msg)

    def update_user_list(self, users):
        """Update the user list with better visibility"""
        self.user_list.clear()
        others = [u for u in users if u != self.username]
        self.online_badge.setText(f"{len(others)} online")
        
        for username in others:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, username)
            
            # Create custom widget for user item with BETTER VISIBILITY
            user_widget = QFrame()
            user_widget.setStyleSheet("""
                QFrame {
                    background: rgba(139, 92, 246, 0.25);
                    border-radius: 14px;
                    border: 1px solid rgba(139, 92, 246, 0.5);
                    margin: 3px;
                }
                QFrame:hover {
                    background: rgba(139, 92, 246, 0.5);
                    border: 1px solid rgba(139, 92, 246, 0.8);
                }
            """)
            
            user_layout = QHBoxLayout(user_widget)
            user_layout.setContentsMargins(14, 12, 14, 12)
            user_layout.setSpacing(14)
            
            # Avatar with gradient
            avatar_frame = QFrame()
            avatar_frame.setFixedSize(42, 42)
            avatar_frame.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #8B5CF6,
                        stop:1 #EC4899);
                    border-radius: 21px;
                    border: 1px solid rgba(255,255,255,0.3);
                }
            """)
            avatar_layout = QVBoxLayout(avatar_frame)
            avatar_layout.setAlignment(Qt.AlignCenter)
            avatar_label = QLabel("👤")
            avatar_label.setStyleSheet("font-size: 20px; background: transparent;")
            avatar_layout.addWidget(avatar_label)
            
            # Username with BRIGHT WHITE color for better visibility
            name_label = QLabel(username)
            name_label.setStyleSheet("""
                QLabel {
                    color: #FFFFFF;
                    font-size: 15px;
                    font-weight: 700;
                    letter-spacing: 0.5px;
                }
            """)
            
            # Status indicator with animation
            status_dot = QFrame()
            status_dot.setFixedSize(12, 12)
            status_dot.setStyleSheet("""
                QFrame {
                    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                        stop:0 #10B981,
                        stop:1 #059669);
                    border-radius: 6px;
                    border: 1px solid rgba(255,255,255,0.3);
                }
            """)
            
            user_layout.addWidget(avatar_frame)
            user_layout.addWidget(name_label, 1)
            user_layout.addWidget(status_dot)
            
            item.setSizeHint(user_widget.sizeHint())
            self.user_list.addItem(item)
            self.user_list.setItemWidget(item, user_widget)

    def show_error(self, msg):
        error_box = QMessageBox(self)
        error_box.setStyleSheet("""
            QMessageBox {
                background: #1E1B4B;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 13px;
            }
            QPushButton {
                background: #8B5CF6;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 8px 20px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #7C3AED;
            }
        """)
        error_box.warning(self, "TalkNest", msg)

    def show_info(self, msg):
        info_box = QMessageBox(self)
        info_box.setStyleSheet("""
            QMessageBox {
                background: #1E1B4B;
            }
            QMessageBox QLabel {
                color: white;
                font-size: 13px;
            }
            QPushButton {
                background: #10B981;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 8px 20px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #059669;
            }
        """)
        info_box.information(self, "TalkNest", msg)

    def kick_selected_user(self):
        item = self.user_list.currentItem()
        if not item:
            self.show_error("Select a user first.")
            return
        target = item.data(Qt.UserRole)
        if target == self.username:
            self.show_error("You cannot kick yourself.")
            return
        self.network_client.kick_user(target)

    def ban_selected_user(self):
        item = self.user_list.currentItem()
        if not item:
            self.show_error("Select a user first.")
            return
        target = item.data(Qt.UserRole)
        if target == self.username:
            self.show_error("You cannot ban yourself.")
            return
        self.network_client.ban_user(target)

    def on_disconnected(self):
        pass

    def closeEvent(self, event):
        self.network_client.disconnect()
        event.accept()