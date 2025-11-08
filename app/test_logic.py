import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# テスト対象のコードを logic.py に保存していると仮定
# （以下のコードを logic.py として保存してください）
# from modules import create_task, task_execute, taskRouter
# ...（ユーザーが提供したコード全体）...

from logic import logic_v1, base_tasks, TASKS_FILE_PATH

# ------------------------------------------------------------
# テストで使う一時ファイル（tasks.json）を tmp_path で管理
# ------------------------------------------------------------
@pytest.fixture
def tasks_path(monkeypatch, tmp_path: Path):
    """TASKS_FILE_PATH を一時ディレクトリに変更"""
    temp_file = tmp_path / "tasks.json"
    monkeypatch.setattr("logic.TASKS_FILE_PATH", str(temp_file))
    return temp_file

# ------------------------------------------------------------
# 1. 単純応答（event_0）が正しく実行される
# ------------------------------------------------------------
def t_simple_response(tasks_path):
    with patch("logic.taskRouter") as mock_router, \
         patch("logic.task_execute") as mock_execute:
        
        mock_router.return_value = "event_0"
        mock_execute.return_value = "こんにちは！元気だよ！"

        result = logic_v1("こんにちは")

        assert result == "こんにちは！元気だよ！"
        mock_router.assert_called_once()
        mock_execute.assert_called_once_with(
            "こんにちは",
            "ユーザーメッセージに対して、応答してください。"
        )

# ------------------------------------------------------------
# 2. 新規タスク作成（event_1）→ 成功パターン
# ------------------------------------------------------------
def t_create_new_task_success(tasks_path):
    # ファイルは最初存在しない
    assert not tasks_path.exists()

    new_task_from_llm = {
        "name": "議事録要約",
        "description": "ユーザーが議事録を送ったら要約する",
        "instruction": "以下の議事録を箇条書きで要約してください。",
        # example_message は任意（taskRouterが使うなら必要）
        "example_message": ["議事録を送ったら、要約して"]
    }

    with patch("logic.taskRouter") as mock_router, \
         patch("logic.create_task") as mock_create, \
         patch("logic.task_execute") as mock_execute:
        
        mock_router.return_value = "event_1"
        mock_create.return_value = new_task_from_llm

        message = "議事録を送ったら、要約して"
        result = logic_v1(message)

        # 戻り値の確認
        expected = (
            "新しくタスクを登録したよ！\n"
            f"タスク名：{new_task_from_llm['name']}\n"
            f"タスクの説明：{new_task_from_llm['description']}"
        )
        assert result == expected

        # ファイルに正しく保存されたか
        with open(tasks_path) as f:
            saved_tasks = json.load(f)
        
        expected_task = new_task_from_llm.copy()
        expected_task["id"] = f"event_{len(base_tasks)}"  # base_tasks は2つあるので event_2
        assert saved_tasks == [expected_task]

        # モックが正しく呼ばれたか
        mock_create.assert_called_once_with(message)
        mock_execute.assert_not_called()

# ------------------------------------------------------------
# 3. 新規タスク作成 → create_task が None を返した場合（失敗）
# ------------------------------------------------------------
def t_create_new_task_fail(tasks_path):
    with patch("logic.taskRouter") as mock_router, \
         patch("logic.create_task") as mock_create:
        
        mock_router.return_value = "event_1"
        mock_create.return_value = None  # LLMが解析失敗したケース

        result = logic_v1("わけわからんメッセージ")

        assert result == "タスクの作成に失敗しました…\nごめんね"
        mock_create.assert_called_once()

# ------------------------------------------------------------
# 4. 登録済みのカスタムタスクが実行される
# ------------------------------------------------------------
def t_execute_custom_task(tasks_path):
    # 事前に tasks.json にカスタムタスクを書き込んでおく
    custom_task = {
        "id": "event_9",
        "name": "ポジティブ変換",
        "description": "ネガティブなメッセージをポジティブに変換",
        "instruction": "以下のメッセージをポジティブに言い換えてください。",
        "example_message": ["メッセージがネガティブだったら、ポジティブに変換して"]
    }
    with open(tasks_path, "w", encoding="utf-8") as f:
        json.dump([custom_task], f, ensure_ascii=False, indent=4)

    with patch("logic.taskRouter") as mock_router, \
         patch("logic.task_execute") as mock_execute:
        
        mock_router.return_value = "event_9"
        mock_execute.return_value = "最高だよ！めっちゃ楽しい！"

        result = logic_v1("最悪だ…もう嫌い…")

        assert result == "最高だよ！めっちゃ楽しい！"
        mock_execute.assert_called_once_with(
            "最悪だ…もう嫌い…",
            "以下のメッセージをポジティブに言い換えてください。"
        )

# ------------------------------------------------------------
# 5. タスクが見つからない（unknown id）
# ------------------------------------------------------------
def t_task_not_found(tasks_path):
    with patch("logic.taskRouter") as mock_router:
        
        mock_router.return_value = "event_999"  # 存在しないID

        result = logic_v1("なんでもいい")

        assert result == "タスクが見つかりませんでした..."
        

# ------------------------------------------------------------
# 6. tasks.json が壊れている（JSONDecodeError）場合も空リストで継続するか確認
# ------------------------------------------------------------
def t_corrupted_json(tasks_path):
    # 壊れたJSONを書き込む
    tasks_path.write_text("これはJSONじゃない", encoding="utf-8")

    with patch("logic.taskRouter") as mock_router, \
         patch("logic.task_execute") as mock_execute:
        
        mock_router.return_value = "event_0"
        mock_execute.return_value = "おはよう！"

        result = logic_v1("おはよう")

        assert result == "おはよう！"
        # 壊れたファイルは無視されて base_tasks のみ使用される