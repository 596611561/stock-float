"""
股价悬浮窗 - Stock Floating
在屏幕左下角（任务栏上方）显示实时股价
类似 TrafficMonitor 的效果
"""

import threading
import time
import json
import os
import re
import datetime
import requests
from pathlib import Path
import tkinter as tk
from tkinter import ttk


CONFIG_FILE = Path(__file__).parent / "stock_config.json"

DEFAULT_CONFIG = {
    "stocks": [
        {"symbol": "300274.SZ", "name": "阳光电源"},
        {"symbol": "600519.SS", "name": "贵州茅台"},
        {"symbol": "AAPL",      "name": "苹果"},
    ],
    "refresh_interval": 30
}

state = {
    "config": {},
    "prices": {},
    "current_index": 0,
    "running": True,
}


def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            for k, v in DEFAULT_CONFIG.items():
                cfg.setdefault(k, v)
            return cfg
        except:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════
#  数据源
# ═══════════════════════════════════════════════════════════════

def fetch_ashare(symbol: str):
    code, market = symbol.rsplit(".", 1)
    prefix = "sh" if market.upper() == "SS" else "sz"
    sina_code = prefix + code
    url = f"https://hq.sinajs.cn/list={sina_code}"
    try:
        resp = requests.get(url, timeout=8, headers={"Referer": "https://finance.sina.com.cn"})
        resp.encoding = "gbk"
        m = re.search(r'"([^"]+)"', resp.text)
        if not m:
            return None
        parts = m.group(1).split(",")
        if len(parts) < 4:
            return None
        price = float(parts[3])
        prev = float(parts[2])
        pct = (price - prev) / prev * 100 if prev else 0
        return price, pct
    except:
        return None


def fetch_overseas(symbol: str):
    s = symbol.upper()
    if s.endswith("-USD"):
        coin = s.replace("-USD", "").lower()
        tx = f"r_{coin}usd"
    else:
        tx = f"us{s}"
    url = f"https://qt.gtimg.cn/q={tx}"
    try:
        resp = requests.get(url, timeout=8)
        resp.encoding = "gbk"
        m = re.search(r'"([^"]+)"', resp.text)
        if not m:
            return None
        parts = m.group(1).split("~")
        if len(parts) < 5:
            return None
        price = float(parts[3])
        prev = float(parts[4]) if parts[4] else 0
        pct = (price - prev) / prev * 100 if prev else 0
        return price, pct
    except:
        return None


def fetch_price(symbol: str):
    s = symbol.upper()
    if s.endswith(".SS") or s.endswith(".SZ"):
        return fetch_ashare(symbol)
    else:
        return fetch_overseas(symbol)


def refresh_all():
    cfg = state["config"]
    for stock in cfg.get("stocks", []):
        symbol = stock["symbol"]
        result = fetch_price(symbol)
        if result:
            price, pct = result
            state["prices"][symbol] = {
                "price": price,
                "change_pct": pct,
                "name": stock.get("name", symbol)
            }
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 刷新完成")


# ═══════════════════════════════════════════════════════════════
#  悬浮窗
# ═══════════════════════════════════════════════════════════════

class FloatingWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("股价")
        self.root.attributes("-topmost", True)       # 始终置顶
        self.root.attributes("-alpha", 0.95)         # 半透明
        self.root.overrideredirect(True)              # 无边框
        self.root.configure(bg="#1e1e1e")
        
        # 样式
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # 主框架
        self.frame = tk.Frame(self.root, bg="#1e1e1e", cursor="hand2")
        self.frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # 关闭按钮
        self.btn_close = tk.Label(
            self.frame, text="✕", bg="#1e1e1e", fg="#888",
            font=("微软雅黑", 8), cursor="hand2"
        )
        self.btn_close.pack(side="right", padx=(5,0))
        self.btn_close.bind("<Button-1>", lambda e: self.on_close())
        
        # 股票名称
        self.lbl_name = tk.Label(
            self.frame, text="加载中...", bg="#1e1e1e", fg="#aaa",
            font=("微软雅黑", 10)
        )
        self.lbl_name.pack(side="left")
        
        # 价格
        self.lbl_price = tk.Label(
            self.frame, text="--", bg="#1e1e1e", fg="#fff",
            font=("微软雅黑", 14, "bold")
        )
        self.lbl_price.pack(side="left", padx=(8,0))
        
        # 涨跌幅
        self.lbl_pct = tk.Label(
            self.frame, text="--", bg="#1e1e1e", fg="#888",
            font=("微软雅黑", 10)
        )
        self.lbl_pct.pack(side="left", padx=(5,0))
        
        # 绑定拖动
        self.frame.bind("<Button-1>", self.start_drag)
        self.frame.bind("<B1-Motion>", self.do_drag)
        self.root.bind("<Button-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.do_drag)
        
        # 右键菜单
        self.menu = tk.Menu(self.root, tearoff=0, bg="#2d2d2d", fg="#ddd")
        self.menu.add_command(label="刷新", command=self.on_refresh)
        self.menu.add_command(label="切换股票", command=self.on_next)
        self.menu.add_separator()
        self.menu.add_command(label="退出", command=self.on_close)
        
        self.frame.bind("<Button-3>", self.show_menu)
        
        # 初始位置
        self.position_window()
        
        # 拖动偏移
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        # 绑定滚轮切换
        self.root.bind("<MouseWheel>", self.on_wheel)
        
    def position_window(self):
        """放在左下角，任务栏上方"""
        self.root.update_idletasks()
        w, h = 200, 36
        x = 0  # 最左边
        # 获取屏幕高度减去任务栏
        screen_h = self.root.winfo_screenheight()
        y = screen_h - h - 48  # 48是任务栏大概高度
        self.root.geometry(f"{w}x{h}+{x}+{y}")
    
    def start_drag(self, event):
        self.drag_offset_x = event.x
        self.drag_offset_y = event.y
    
    def do_drag(self, event):
        x = self.root.winfo_x() + event.x - self.drag_offset_x
        y = self.root.winfo_y() + event.y - self.drag_offset_y
        self.root.geometry(f"+{x}+{y}")
    
    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)
    
    def on_refresh(self):
        refresh_all()
        self.update_display()
    
    def on_next(self):
        n = len(state["config"].get("stocks", []))
        if n:
            state["current_index"] = (state["current_index"] + 1) % n
            self.update_display()
    
    def on_wheel(self, event):
        """滚轮切换股票"""
        n = len(state["config"].get("stocks", []))
        if n:
            if event.delta > 0:
                state["current_index"] = (state["current_index"] - 1) % n
            else:
                state["current_index"] = (state["current_index"] + 1) % n
            self.update_display()
    
    def on_close(self):
        state["running"] = False
        self.root.destroy()
    
    def update_display(self):
        cfg = state["config"]
        stocks = cfg.get("stocks", [])
        if not stocks:
            self.lbl_name.config(text="无股票")
            self.lbl_price.config(text="--")
            self.lbl_pct.config(text="")
            return
        
        idx = state["current_index"] % len(stocks)
        stock = stocks[idx]
        data = state["prices"].get(stock["symbol"])
        name = stock.get("name", stock["symbol"])
        
        self.lbl_name.config(text=name)
        
        if data:
            price = data["price"]
            pct = data["change_pct"]
            sign = "+" if pct >= 0 else ""
            
            # 价格
            self.lbl_price.config(text=f"{price:.2f}")
            
            # 涨跌幅颜色
            if pct >= 0:
                color = "#dc6f6f"  # 红涨
            else:
                color = "#6fdc8c"  # 绿跌
            self.lbl_pct.config(text=f"{sign}{pct:.2f}%", fg=color)
        else:
            self.lbl_price.config(text="加载中")
            self.lbl_pct.config(text="", fg="#888")
    
    def run(self):
        self.update_display()
        self.root.mainloop()


# ═══════════════════════════════════════════════════════════════
#  后台刷新
# ═══════════════════════════════════════════════════════════════

def background_refresh(window: FloatingWindow):
    interval = state["config"].get("refresh_interval", 30)
    while state["running"]:
        time.sleep(interval)
        if state["running"]:
            refresh_all()
            window.root.after(0, window.update_display)


# ═══════════════════════════════════════════════════════════════
#  主程序
# ═══════════════════════════════════════════════════════════════

def main():
    print("=" * 50)
    print("  股价悬浮窗 启动中...")
    print("=" * 50)
    
    cfg = load_config()
    state["config"] = cfg
    save_config(cfg)
    
    print("正在获取股价...")
    refresh_all()
    
    window = FloatingWindow()
    
    threading.Thread(target=background_refresh, args=(window,), daemon=True).start()
    
    print("启动成功！拖动可移动位置，滚轮切换股票")
    window.run()


if __name__ == "__main__":
    main()
