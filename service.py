"""GUI operations over the existing verified installer and its recovery journal."""
import hashlib
import json
import os
from pathlib import Path
import manage


def data_root():
    return Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "ZhangxinPlus"


def settings_path():
    return data_root() / "gui.json"


def load_game():
    try:
        value = json.loads(settings_path().read_text("utf8"))
        return str(value.get("game", ""))
    except (OSError, ValueError):
        return ""


def normalize_game(value):
    game = Path(value).expanduser().resolve()
    if game.is_file() and game.name.lower() == "zhangxinmj.exe":
        game = game.parent
    if not (game / "zhangxinmj.exe").is_file():
        raise ValueError("请选择包含 zhangxinmj.exe 的掌心安装目录。")
    return game


def choose_state(game, *, local=None, roaming=None):
    game = game.resolve()
    local = local or data_root()
    roaming = roaming or Path(os.environ.get("APPDATA", str(Path.home())))
    key = hashlib.sha256(str(game).casefold().encode()).hexdigest()[:16]
    dedicated = local / "installs" / key
    # Reuse a matching journal; never replace an unrelated installation's backup.
    candidates = [roaming / "akagiplus" / "zhangxinplus", local, dedicated]
    for candidate in candidates:
        journal = candidate / "install.json"
        if not journal.is_file():
            continue
        try:
            record = json.loads(journal.read_text("utf8"))
            owner = Path(record["game"]).resolve()
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise ValueError("发现无法读取的恢复记录，请保留备份并先排查：" + str(journal)) from exc
        if owner == game:
            return candidate
        if candidate == dedicated:
            raise ValueError("备份目录与游戏路径不一致，请保留原始恢复记录。")
    return dedicated


def perform(action, value):
    game = normalize_game(value)
    state = choose_state(game)
    journal = state / "install.json"
    if action == "install":
        manage.prepare_install(game, state / "staged", journal)
    elif action == "restore":
        if not journal.is_file():
            raise ValueError("找不到这个游戏目录的原始备份，不能还原。")
        manage.restore(game, journal)
    elif action != "status":
        raise ValueError("未知操作。")
    result = manage.status(game, journal)
    if action == "install":
        result["message"] = "安装 / 更新完成，请重新启动掌心。"
    elif action == "restore":
        result["message"] = "已还原游戏文件；本地装扮选择和原始备份保留。"
    # Save only the local installation path; no account or game payload is copied.
    manage.atomic(settings_path(), json.dumps({"game": str(game)}, ensure_ascii=False).encode("utf8"))
    return {**result, "game": str(game), "state": str(state)}


def friendly_error(exc):
    message = str(exc)
    if "Close Zhangxin" in message:
        return "请先正常退出掌心，再安装、更新或还原。"
    if "Backup checksum" in message or "backup checksum" in message:
        return "原始备份校验失败。请保留备份目录，不要覆盖或删除。"
    if "Game updated or changed" in message or "Unreviewed" in message:
        return "游戏资源已更新或被其他工具修改。本工具已停止覆盖，请等待适配。"
    return message or type(exc).__name__
