import time
import tkinter as tk
import unittest
from unittest.mock import patch
import gui


class WorkerRecovery(unittest.TestCase):
    def test_failed_background_action_reenables_window(self):
        root = tk.Tk(); root.withdraw()
        try:
            with patch.object(gui.service, "load_game", return_value=""):
                app = gui.Application(root)
            app.game.set("synthetic-game")
            with patch.object(gui.service, "perform", side_effect=ValueError("test failure")):
                app.start("install")
                self.assertTrue(app.busy)
                deadline = time.monotonic() + 3
                while app.busy and time.monotonic() < deadline:
                    root.update(); time.sleep(.02)
            self.assertFalse(app.busy)
            self.assertIn("test failure", app.status.get())
            self.assertTrue(all(str(button["state"]) == "normal" for button in app.buttons))
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
