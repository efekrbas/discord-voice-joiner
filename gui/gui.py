import sys
import asyncio
import os
import random
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QFrame, QPushButton, QLabel, QLineEdit, QStackedWidget, 
    QScrollArea, QSizePolicy, QFrame, QGridLayout, QComboBox
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette
from qasync import QEventLoop, asyncSlot

from bot_manager import BotManager
from discord_api import check_token

# AMOLED Black Theme
DARK_STYLE = """
QMainWindow, QWidget { background-color: #000000; color: #e0e0e0; border: none; }
QFrame#Sidebar { background-color: #050505; border-right: 1px solid #111111; }
QFrame#StatCard, QFrame#BotRow { background-color: #0a0a0a; border-radius: 12px; border: 1px solid #1a1a1a; }
QPushButton { background-color: #3a86ff; color: white; border-radius: 6px; padding: 8px 16px; font-weight: bold; border: none; }
QPushButton:hover { background-color: #559aff; }
QPushButton#NavBtn { background-color: transparent; text-align: left; padding: 12px 20px; font-size: 14px; color: #888; }
QPushButton#NavBtn:hover { background-color: #111111; color: #fff; }
QPushButton#NavBtn[active="true"] { background-color: #1a1a1a; border-left: 4px solid #3a86ff; color: #fff; }
QPushButton#IconBtn { background-color: #1a1a1a; padding: 5px; font-size: 16px; border: 1px solid #222; }
QPushButton#IconBtn:hover { background-color: #3a86ff; }
QPushButton#BulkBtn { background-color: #1a1a1a; color: #aaa; border: 1px solid #222; }
QPushButton#BulkBtn:hover { background-color: #2a2a2a; color: #fff; }
QPushButton[styleClass="success"] { background-color: #1b5e20; }
QPushButton[styleClass="success"]:hover { background-color: #27ae60; }
QPushButton[styleClass="danger"] { background-color: #b71c1c; }
QPushButton[styleClass="danger"]:hover { background-color: #e74c3c; }
QLineEdit { background-color: #050505; color: white; border: 1px solid #1a1a1a; border-radius: 6px; padding: 8px; }
QLabel { color: #e0e0e0; background: transparent; }
QScrollArea, QScrollArea QWidget { background-color: #000000; border: none; }
QScrollBar:vertical { background: #000000; width: 10px; }
QScrollBar::handle:vertical { background: #1a1a1a; border-radius: 5px; }
QComboBox { background-color: #0d0d0d; color: white; border: 1px solid #1a1a1a; border-radius: 4px; padding: 5px 10px; min-width: 150px; }
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView { background-color: #0d0d0d; color: white; selection-background-color: #3a86ff; border: 1px solid #1a1a1a; outline: none; }
"""

# Full White Theme
LIGHT_STYLE = """
QMainWindow, QWidget { background-color: #ffffff; color: #000000; border: none; }
QFrame#Sidebar { background-color: #f8f9fa; border-right: 1px solid #e9ecef; }
QFrame#StatCard, QFrame#BotRow { background-color: #f1f3f5; border-radius: 12px; border: 1px solid #dee2e6; }
QPushButton { background-color: #3a86ff; color: white; border-radius: 6px; padding: 8px 16px; font-weight: bold; border: none; }
QPushButton:hover { background-color: #559aff; }
QPushButton#NavBtn { background-color: transparent; text-align: left; padding: 12px 20px; font-size: 14px; color: #495057; }
QPushButton#NavBtn:hover { background-color: #e9ecef; color: #000; }
QPushButton#NavBtn[active="true"] { background-color: #dee2e6; border-left: 4px solid #3a86ff; color: #000; }
QPushButton#IconBtn { background-color: #ffffff; padding: 5px; font-size: 16px; border: 1px solid #dee2e6; color: #333; }
QPushButton#IconBtn:hover { background-color: #3a86ff; border: 1px solid #3a86ff; color: white; }
QPushButton#BulkBtn { background-color: #f1f3f5; color: #495057; border: 1px solid #dee2e6; }
QPushButton#BulkBtn:hover { background-color: #e9ecef; }
QPushButton[styleClass="success"] { background-color: #2ecc71; }
QPushButton[styleClass="danger"] { background-color: #e74c3c; }
QLineEdit { background-color: #ffffff; color: #000000; border: 1px solid #dee2e6; border-radius: 6px; padding: 8px; }
QLabel { color: #212529; background: transparent; }
QScrollArea, QScrollArea QWidget { background-color: #ffffff; border: none; }
QScrollBar:vertical { background: #ffffff; width: 10px; }
QScrollBar::handle:vertical { background: #dee2e6; border-radius: 5px; }
QComboBox { background-color: #ffffff; color: black; border: 1px solid #ced4da; border-radius: 4px; padding: 5px 10px; min-width: 150px; }
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView { background-color: #ffffff; color: black; selection-background-color: #e9ecef; border: 1px solid #ced4da; outline: none; }
QPushButton#BulkBtn { background-color: #e9ecef; color: #495057; border: 1px solid #dee2e6; }
QPushButton#BulkBtn:hover { background-color: #dee2e6; color: #212529; }
"""

class MainWindow(QMainWindow):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.tokens = []
        
        self.setWindowTitle("Discord Voice Manager")
        if os.path.exists("icon.ico"):
            self.setWindowIcon(QIcon("icon.ico"))
        self.resize(1200, 750)

        # Central Widget & Main Layout
        self.central_widget = QWidget()
        self.central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(self.central_widget)
        
        # Core Layout (Vertical to allow Footer)
        self.core_layout = QVBoxLayout(self.central_widget)
        self.core_layout.setContentsMargins(0, 0, 0, 0)
        self.core_layout.setSpacing(0)

        # Top Container (Sidebar + Content)
        self.top_container = QWidget()
        self.main_layout = QHBoxLayout(self.top_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.core_layout.addWidget(self.top_container)

        # Footer Area
        self.footer = QFrame()
        self.footer.setFixedHeight(40)
        self.footer_layout = QHBoxLayout(self.footer)
        self.footer_layout.setContentsMargins(20, 0, 20, 5)
        
        about_lbl = QLabel("Manage your Discord accounts voice activity 24/7")
        about_lbl.setStyleSheet("color: #555; font-size: 10px; font-style: italic;")
        self.footer_layout.addWidget(about_lbl)
        self.footer_layout.addStretch()
        
        self.credit_lbl = QLabel("Developed by Efe Kırbaş")
        self.credit_lbl.setFont(QFont("Outfit", 9))
        self.credit_lbl.setStyleSheet("color: #888; font-weight: bold; font-size: 11px;")
        self.footer_layout.addWidget(self.credit_lbl)
        
        self.core_layout.addWidget(self.footer)

        # Sidebar
        self.setup_sidebar()

        # Content Area (Stacked Widget)
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("MainContent")
        self.main_layout.addWidget(self.content_stack)

        self.setup_dashboard()
        self.setup_management()

        self.load_tokens()
        self.switch_page(0)
        
        # Apply Default Theme (AMOLED)
        self.setStyleSheet(DARK_STYLE)

        # UI Update Timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_stats)
        self.update_timer.start(5000)

    def setup_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)

        self.logo = QLabel("VOICE MANAGER")
        self.logo.setFont(QFont("Outfit", 18, QFont.Weight.Bold))
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo.setStyleSheet("margin-bottom: 30px; color: #3a86ff; background: transparent;")
        sidebar_layout.addWidget(self.logo)

        self.nav_btns = []
        self.btn_dashboard = self.create_nav_btn("Dashboard", 0, sidebar_layout)
        self.btn_accounts = self.create_nav_btn("Accounts", 1, sidebar_layout)

        sidebar_layout.addStretch()

        self.theme_lbl = QLabel("Appearance Mode:")
        self.theme_lbl.setStyleSheet("margin-left: 20px; font-size: 11px; background: transparent;")
        sidebar_layout.addWidget(self.theme_lbl)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setContentsMargins(20, 0, 20, 20)
        self.theme_combo.currentTextChanged.connect(self.handle_theme_change)
        sidebar_layout.addWidget(self.theme_combo)
        sidebar_layout.addSpacing(20)

        self.main_layout.addWidget(self.sidebar)

    def create_nav_btn(self, text, index, layout):
        btn = QPushButton(text)
        btn.setObjectName("NavBtn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda: self.switch_page(index))
        layout.addWidget(btn)
        self.nav_btns.append(btn)
        return btn

    def switch_page(self, index):
        self.content_stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_btns):
            btn.setProperty("active", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        if index == 1: self.refresh_management_table()

    def handle_theme_change(self, mode):
        if "Light" in mode:
            self.setStyleSheet(LIGHT_STYLE)
        else:
            self.setStyleSheet(DARK_STYLE)

    # --- Dashboard ---
    def setup_dashboard(self):
        page = QWidget()
        page.setObjectName("MainContent")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("Dashboard")
        title.setFont(QFont("Outfit", 24, QFont.Weight.Bold))
        layout.addWidget(title)

        stats_row = QHBoxLayout()
        self.lbl_total_tokens = self.create_stat_card("Total Tokens", "0", stats_row)
        self.lbl_active_tokens = self.create_stat_card("Active Tokens", "0", stats_row)
        stats_row.addStretch()
        layout.addLayout(stats_row)

        layout.addSpacing(40)

        join_group = QFrame()
        join_group.setObjectName("StatCard")
        join_layout = QVBoxLayout(join_group)
        join_layout.setContentsMargins(20, 20, 20, 20)

        jl = QLabel("Bulk Voice Join")
        jl.setFont(QFont("Outfit", 14, QFont.Weight.Bold))
        join_layout.addWidget(jl)

        self.entry_guild = QLineEdit()
        self.entry_guild.setPlaceholderText("Server ID")
        self.entry_guild.setFixedWidth(400)
        join_layout.addWidget(self.entry_guild)

        self.entry_channel = QLineEdit()
        self.entry_channel.setPlaceholderText("Voice Channel ID")
        self.entry_channel.setFixedWidth(400)
        join_layout.addWidget(self.entry_channel)

        btn_row = QHBoxLayout()
        btn_join = QPushButton("Join All")
        btn_join.setProperty("styleClass", "success")
        btn_join.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_join.clicked.connect(self.bulk_join_all)
        btn_row.addWidget(btn_join)

        btn_stop = QPushButton("Stop All")
        btn_stop.setProperty("styleClass", "danger")
        btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_stop.clicked.connect(self.bulk_stop_all)
        btn_row.addWidget(btn_stop)
        btn_row.addStretch()
        join_layout.addLayout(btn_row)

        layout.addWidget(join_group)

        actions_group = QFrame()
        actions_group.setObjectName("StatCard")
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.setContentsMargins(20, 20, 20, 20)

        al = QLabel("Bulk Account Controls")
        al.setFont(QFont("Outfit", 14, QFont.Weight.Bold))
        actions_layout.addWidget(al)

        grid = QGridLayout()
        grid.addWidget(self.create_bulk_btn("Mute All", lambda: self.bulk_audio(True, None)), 0, 0)
        grid.addWidget(self.create_bulk_btn("Unmute All", lambda: self.bulk_audio(False, None)), 0, 1)
        grid.addWidget(self.create_bulk_btn("Deafen All", lambda: self.bulk_audio(None, True)), 0, 2)
        grid.addWidget(self.create_bulk_btn("Undeafen All", lambda: self.bulk_audio(None, False)), 0, 3)
        grid.addWidget(self.create_bulk_btn("Mute & Deafen All", lambda: self.bulk_audio(True, True)), 1, 0)
        grid.addWidget(self.create_bulk_btn("Unmute & Undeafen All", lambda: self.bulk_audio(False, False)), 1, 1)
        grid.addWidget(self.create_bulk_btn("Video ON All", lambda: self.bulk_video(True)), 1, 2)
        grid.addWidget(self.create_bulk_btn("Stream ON All", lambda: self.bulk_stream(True)), 1, 3)
        grid.addWidget(self.create_bulk_btn("Video OFF All", lambda: self.bulk_video(False)), 2, 0)
        grid.addWidget(self.create_bulk_btn("Stream OFF All", lambda: self.bulk_stream(False)), 2, 1)
        actions_layout.addLayout(grid)

        layout.addWidget(actions_group)
        layout.addStretch()
        self.content_stack.addWidget(page)

    def create_stat_card(self, title, value, layout):
        card = QFrame()
        card.setObjectName("StatCard")
        card.setFixedSize(200, 100)
        card_layout = QVBoxLayout(card)
        tl = QLabel(title); tl.setAlignment(Qt.AlignmentFlag.AlignCenter); tl.setStyleSheet("font-size: 11px; background: transparent;"); card_layout.addWidget(tl)
        vl = QLabel(value); vl.setAlignment(Qt.AlignmentFlag.AlignCenter); vl.setFont(QFont("Outfit", 24, QFont.Weight.Bold)); vl.setStyleSheet("color: #3a86ff; background: transparent;"); card_layout.addWidget(vl)
        layout.addWidget(card)
        return vl

    def create_bulk_btn(self, text, func):
        btn = QPushButton(text)
        btn.setObjectName("BulkBtn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(func)
        return btn

    # --- Accounts ---
    def setup_management(self):
        page = QWidget()
        page.setObjectName("MainContent")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        header = QHBoxLayout()
        title = QLabel("Account Management"); title.setFont(QFont("Outfit", 24, QFont.Weight.Bold)); header.addWidget(title)
        refresh_btn = QPushButton("Refresh List"); refresh_btn.setFixedWidth(120); refresh_btn.clicked.connect(self.refresh_management_table); header.addWidget(refresh_btn)
        layout.addLayout(header)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True); self.scroll_content = QWidget(); self.scroll_layout = QVBoxLayout(self.scroll_content); self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop); self.scroll.setWidget(self.scroll_content); layout.addWidget(self.scroll)
        self.content_stack.addWidget(page)

    def refresh_management_table(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()
        for token in self.tokens:
            bot = self.manager.bots.get(token) or self.manager.add_token(token)
            row = QFrame(); row.setObjectName("BotRow"); row_layout = QHBoxLayout(row)
            info = QLabel(f"{token[:12]}..."); info.setFixedWidth(100); row_layout.addWidget(info)
            status = QLabel(bot.status); status.setFixedWidth(100); status.setStyleSheet("color: #27ae60;" if "Connected" in bot.status else "color: #888;"); row_layout.addWidget(status)
            # Controls
            ctrl_layout = QHBoxLayout()
            m_btn = self.create_icon_btn("🎤" if not bot.self_mute else "🔇", lambda _, b=bot: self.toggle_mute(b))
            h_btn = self.create_icon_btn("🎧" if not bot.self_deaf else "❌", lambda _, b=bot: self.toggle_deafen(b))
            both_btn = self.create_icon_btn("🔒" if not (bot.self_mute and bot.self_deaf) else "🔓", lambda _, b=bot: self.toggle_both(b))
            c_btn = self.create_icon_btn("📷" if not bot.self_video else "📽️", lambda _, b=bot: self.toggle_video(b))
            s_btn = self.create_icon_btn("📺" if not bot.self_stream else "🎬", lambda _, b=bot: self.toggle_stream(b))
            
            ctrl_layout.addWidget(m_btn); ctrl_layout.addWidget(h_btn); ctrl_layout.addWidget(both_btn); ctrl_layout.addWidget(c_btn); ctrl_layout.addWidget(s_btn); row_layout.addLayout(ctrl_layout); row_layout.addStretch()
            g_in = QLineEdit(); g_in.setPlaceholderText("Server ID"); g_in.setFixedWidth(120); g_in.setText(str(bot.guild_id) if bot.guild_id else ""); row_layout.addWidget(g_in)
            c_in = QLineEdit(); c_in.setPlaceholderText("Channel ID"); c_in.setFixedWidth(120); c_in.setText(str(bot.channel_id) if bot.channel_id else ""); row_layout.addWidget(c_in)
            j_btn = QPushButton("Join"); j_btn.setProperty("styleClass", "success"); j_btn.clicked.connect(lambda _, b=bot, gi=g_in, ci=c_in: self.single_join(b, gi.text(), ci.text())); row_layout.addWidget(j_btn)
            l_btn = QPushButton("Leave"); l_btn.setProperty("styleClass", "danger"); l_btn.clicked.connect(lambda _, b=bot: self.single_leave(b)); row_layout.addWidget(l_btn)
            self.scroll_layout.addWidget(row)

    def create_icon_btn(self, icon, func):
        btn = QPushButton(icon); btn.setObjectName("IconBtn"); btn.setFixedSize(35, 35); btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if func: btn.clicked.connect(func)
        return btn

    # --- Async Actions ---
    @asyncSlot()
    async def bulk_join_all(self):
        g, c = self.entry_guild.text(), self.entry_channel.text()
        if g and c: await self.manager.join_all(g, c)

    @asyncSlot()
    async def bulk_stop_all(self): await self.manager.stop_all()

    @asyncSlot()
    async def bulk_audio(self, m, d):
        for b in self.manager.bots.values(): await b.update_audio(mute=m, deaf=d)
        self.refresh_management_table()

    @asyncSlot()
    async def bulk_video(self, s):
        for b in self.manager.bots.values(): await b.update_video(video=s)
        self.refresh_management_table()

    @asyncSlot()
    async def bulk_stream(self, s):
        for b in self.manager.bots.values(): await b.update_stream(stream=s)
        self.refresh_management_table()

    @asyncSlot()
    async def toggle_mute(self, b): await b.update_audio(mute=not b.self_mute); self.refresh_management_table()

    @asyncSlot()
    async def toggle_deafen(self, b): await b.update_audio(deaf=not b.self_deaf); self.refresh_management_table()

    @asyncSlot()
    async def toggle_both(self, b):
        state = not (b.self_mute and b.self_deaf)
        await b.update_audio(mute=state, deaf=state)
        self.refresh_management_table()

    @asyncSlot()
    async def toggle_video(self, b): await b.update_video(video=not b.self_video); self.refresh_management_table()

    @asyncSlot()
    async def toggle_stream(self, b):
        await b.update_stream(stream=not b.self_stream)
        self.refresh_management_table()

    @asyncSlot()
    async def single_join(self, b, gi, ci):
        if gi and ci: await b.join_channel(gi, ci); self.refresh_management_table()

    @asyncSlot()
    async def single_leave(self, b): await b.leave_channel(); self.refresh_management_table()

    def load_tokens(self):
        if os.path.exists("tokens.txt"):
            with open("tokens.txt", "r") as f:
                for line in f:
                    clean_line = line.strip()
                    if not clean_line or clean_line.startswith("//"):
                        continue
                    t = clean_line.strip('"').strip("'").strip()
                    if t:
                        self.tokens.append(t)
                        self.manager.add_token(t)
            self.lbl_total_tokens.setText(str(len(self.tokens)))

    def refresh_stats(self):
        active = sum(1 for b in self.manager.bots.values() if b.status == "Connected")
        self.lbl_active_tokens.setText(str(active))

def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    manager = BotManager()
    win = MainWindow(manager)
    win.show()
    with loop: loop.run_forever()

if __name__ == "__main__":
    main()
