import json
from modules import create_task, task_execute, taskRouter

TASKS_FILE_PATH = "tasks.json"  # タスクの保存先ファイルパス

base_tasks = [
    {
      "id": "event_0",
      "name": "単純応答",
      "description": "このイベントは、ユーザーのメッセージに対して単純な応答を返すものです。他のイベントが適用できない場合に使用されます。",
      "instruction": "ユーザーメッセージに対して、応答してください。",
      "example_message": [
        "こんにちは", 
        "おはよう", 
        "こんばんは",
        "元気？",
        "調子はどう？",
        "最近どう？",
        "お疲れ様です",
        "おやすみなさい",
        ]
    },
    {
      "id": "event_1",
      "name": "新規タスク作成。",
      "description": "ユーザーがこれから、ボットに新しくタスクの実行を求めた時に、実行するイベントです。何かを条件に、何かを実行して欲しい場合に、実行するイベントです。",
      "example_message": [
        "議事録を送ったら、要約して", 
        "これから、メールを添削してと言ったら、添削して",
        "メッセージがネガティブだったら、ポジティブに変換して",
        ]
    },
]


def logic_v1(message):
    created_tasks = []
    try:
        with open(TASKS_FILE_PATH, 'r', encoding='utf-8') as f:
            created_tasks = json.load(f)
    except FileNotFoundError: # ファイルが存在しない場合は空のまま
        pass    
    
    tasks = base_tasks + created_tasks

    task_id_str = taskRouter(message, tasks)
    print("\ntask_id_str:")
    print(task_id_str)

    # 新規タスクの作成
    if task_id_str == "event_1":
        print("\n新規タスクの作成")
        task_json_none = create_task(message)

        print("\ntask_json_none")
        print(task_json_none)

        if(task_json_none == None):
            return "タスクの作成に失敗しました…\nごめんね"

        task_json = task_json_none
        task_json["id"] = "event_"+str(len(tasks)) #IDの付与

        # タスクの保存
        created_tasks.append(task_json)
        with open(TASKS_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(created_tasks, f, ensure_ascii=False, indent=4)

        return f"新しくタスクを登録したよ！\nタスク名：{task_json['name']}\nタスクの説明：{task_json['description']}"


    # タスクの実行
    target_task = None
    for task in tasks:
        if task["id"] == task_id_str:
            target_task = task
            break

    if target_task is None:
        return "タスクが見つかりませんでした..."
    
    res = task_execute(message, target_task["instruction"])
    return res


