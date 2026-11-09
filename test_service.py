import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import service


class BackupSelection(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.game = self.root / "game"; self.game.mkdir()
        (self.game / "zhangxinmj.exe").touch()
        self.local = self.root / "local"; self.roaming = self.root / "roaming"

    def tearDown(self):
        self.temp.cleanup()

    def choose(self):
        return service.choose_state(self.game, local=self.local, roaming=self.roaming)

    def journal(self, state, game):
        state.mkdir(parents=True)
        (state / "install.json").write_text(json.dumps({"game": str(game)}))

    def test_reuses_matching_akagiplus_recovery(self):
        shared = self.roaming / "akagiplus" / "zhangxinplus"
        self.journal(shared, self.game)
        self.assertEqual(self.choose(), shared)

    def test_other_installations_do_not_share_backup_directory(self):
        shared = self.roaming / "akagiplus" / "zhangxinplus"
        self.journal(shared, self.root / "other")
        chosen = self.choose()
        self.assertEqual(chosen.parent, self.local / "installs")
        other = service.choose_state(self.root / "other2", local=self.local, roaming=self.roaming)
        self.assertNotEqual(chosen, other)
        self.assertFalse(chosen.exists())

    def test_reuses_legacy_standalone_record(self):
        self.journal(self.local, self.game)
        self.assertEqual(self.choose(), self.local)

    def test_corrupt_journal_stops_before_replacing_backups(self):
        self.local.mkdir(); (self.local / "install.json").write_text("broken")
        with self.assertRaises(ValueError):
            self.choose()
        self.assertEqual((self.local / "install.json").read_text(), "broken")

    def test_install_failure_does_not_save_or_report_success(self):
        with patch.object(service, "choose_state", return_value=self.local), patch.object(service.manage, "prepare_install", side_effect=ValueError("simulated failure")), patch.object(service.manage, "atomic") as save:
            with self.assertRaisesRegex(ValueError, "simulated failure"):
                service.perform("install", str(self.game))
            save.assert_not_called()

    def test_executable_selection_normalizes_to_game_directory(self):
        self.assertEqual(service.normalize_game(str(self.game / "zhangxinmj.exe")), self.game.resolve())


if __name__ == "__main__":
    unittest.main()
