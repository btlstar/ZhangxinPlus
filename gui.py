"""Standalone ZhangxinPlus desktop manager; no game or proxy automation."""
import os
from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import filedialog, ttk
import service
from tool_version import TOOL_VERSION, CORE_VERSION


class Application(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=24)
        self.pack(fill="both", expand=True)
        self.events = queue.Queue()
        self.busy = False
        self.state_dir = None
        self.game = tk.StringVar(value=service.load_game())
        self.status = tk.StringVar(value="请选择掌心全民麻将安装目录，然后查看状态。")
        self.backup = tk.StringVar(value="安装前自动备份；还原时保留本地装扮选择。")
        ttk.Label(self, text="掌心 Plus", font=("Microsoft YaHei UI", 22, "bold")).pack(anchor="w")
        ttk.Label(self, text=f"ZhangxinPlus {TOOL_VERSION}  ·  插件核心 {CORE_VERSION}  ·  资源 92217").pack(anchor="w", pady=(4, 24))
        ttk.Label(self, text="掌心全民麻将安装目录（包含 zhangxinmj.exe）").pack(anchor="w")
        row = ttk.Frame(self); row.pack(fill="x", pady=(8, 20))
        self.entry = ttk.Entry(row, textvariable=self.game)
        self.entry.pack(side="left", fill="x", expand=True, ipady=4)
        self.browse_button = ttk.Button(row, text="选择目录…", command=self.browse)
        self.browse_button.pack(side="left", padx=(10, 0))
        panel = ttk.LabelFrame(self, text="插件状态", padding=16)
        panel.pack(fill="x")
        ttk.Label(panel, textvariable=self.status, wraplength=630, justify="left").pack(anchor="w")
        self.progress = ttk.Progressbar(panel, mode="indeterminate")
        self.progress.pack(fill="x", pady=(14, 0))
        actions = ttk.Frame(self); actions.pack(fill="x", pady=(22, 18))
        self.buttons = []
        for label, action in [("查看状态", "status"), ("安装 / 更新", "install"), ("还原游戏文件", "restore")]:
            button = ttk.Button(actions, text=label, command=lambda a=action: self.start(a))
            button.pack(side="left", padx=(0, 12), ipadx=10, ipady=5)
            self.buttons.append(button)
        ttk.Label(self, text="完成官方资源更新并退出游戏后再安装。安装后正常启动掌心全民麻将，在游戏原有界面选择装扮。", wraplength=660).pack(anchor="w", pady=(0, 12))
        ttk.Label(self, textvariable=self.backup, wraplength=660, foreground="#666666").pack(anchor="w")
        self.open_backup = ttk.Button(self, text="打开备份目录", command=self.show_backup, state="disabled")
        self.open_backup.pack(anchor="w", pady=(10, 0))
        ttk.Label(self, text="安装后在游戏原有界面选择装扮；本地选择按游戏账号保存。", wraplength=660, foreground="#666666").pack(anchor="w", pady=(24, 0))
        master.protocol("WM_DELETE_WINDOW", self.close)
        self.after(100, self.receive)
        if self.game.get():
            self.after(200, lambda: self.start("status"))

    def browse(self):
        value = filedialog.askdirectory(parent=self, title="选择掌心全民麻将安装目录", initialdir=self.game.get() or None)
        if value:
            self.game.set(value)
            self.start("status")

    def start(self, action):
        if self.busy:
            return
        if not self.game.get().strip():
            self.status.set("请先选择掌心全民麻将安装目录。")
            return
        self.busy = True
        for widget in self.buttons + [self.browse_button, self.entry, self.open_backup]:
            widget.configure(state="disabled")
        self.status.set({"status": "正在检查…", "install": "正在核验、备份并安装，请稍候…", "restore": "正在核验并还原，请稍候…"}[action])
        self.progress.start(12)
        value = self.game.get().strip()
        def work():
            try:
                self.events.put((True, service.perform(action, value)))
            except Exception as exc:
                self.events.put((False, service.friendly_error(exc)))
        threading.Thread(target=work, daemon=True).start()

    def receive(self):
        try:
            ok, result = self.events.get_nowait()
        except queue.Empty:
            pass
        else:
            self.busy = False
            self.progress.stop()
            for widget in self.buttons + [self.browse_button, self.entry]:
                widget.configure(state="normal")
            if ok:
                self.status.set(result["message"])
                self.game.set(result["game"])
                self.state_dir = Path(result["state"])
                self.backup.set("备份位置：" + str(self.state_dir))
            else:
                self.status.set("操作未完成：" + result)
            if self.state_dir and self.state_dir.is_dir():
                self.open_backup.configure(state="normal")
        self.after(100, self.receive)

    def show_backup(self):
        if self.state_dir and self.state_dir.is_dir():
            os.startfile(self.state_dir)

    def close(self):
        if self.busy:
            self.status.set("操作正在进行，请完成后再关闭窗口。")
            return
        self.master.destroy()


def main():
    root = tk.Tk()
    root.title(f"ZhangxinPlus {TOOL_VERSION}")
    root.geometry("780x620")
    root.minsize(740, 600)
    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")
    style.configure(".", font=("Microsoft YaHei UI", 10))
    Application(root)
    root.mainloop()


if __name__ == "__main__":
    main()
