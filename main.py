import tkinter as tk
from tkinter import scrolledtext
import threading
import ollama
import requests
import json
import winsound
import os

# --- 設定部分 ---
VOICEVOX_URL = "http://127.0.0.1:50021"
SPEAKER_ID = 47 # ナースロボ＿タイプＴ
MODEL_NAME = "hf.co/mmnga/shisa-v2-qwen2.5-7b-gguf" # Shisaモデル

SYSTEM_PROMPT = """
あなたは超フレンドリーで明るいギャルの友達です！
以下のルールを絶対に守って会話してください。
・AIやプログラムとしての振る舞いは一切禁止。
・完全なタメ口で、親友のように接すること。
・ノリ良く、短くテンポの良い返事をすること。
・「まじで」「ウケる」「超」「やば」「〜っしょ」「〜じゃん」などを自然に使うこと。
"""

chat_history = [{'role': 'system', 'content': SYSTEM_PROMPT}]

# --- 音声再生（変更なし） ---
def play_voice(text):
    if not text.strip(): return
    params = {'text': text, 'speaker': SPEAKER_ID}
    res_query = requests.post(f"{VOICEVOX_URL}/audio_query", params=params)
    if res_query.status_code != 200: return
    res_synth = requests.post(
        f"{VOICEVOX_URL}/synthesis", params={'speaker': SPEAKER_ID},
        data=json.dumps(res_query.json()), headers={'Content-Type': 'application/json'}
    )
    wav_file = "temp_voice.wav"
    with open(wav_file, "wb") as f: f.write(res_synth.content)
    winsound.PlaySound(wav_file, winsound.SND_FILENAME)
    if os.path.exists(wav_file): os.remove(wav_file)

# --- ここからUIとAIの連携処理 ---
def send_message(event=None):
    # 入力欄から文字を取得
    user_input = entry_box.get()
    if not user_input.strip(): return
    
    # 入力欄を空にして、画面に自分の発言を表示
    entry_box.delete(0, tk.END)
    update_chat_area(f"あなた: {user_input}\n")
    
    # ★ 魔法の1行 ★
    # 画面がフリーズしないように、AIの処理を「裏の係（別スレッド）」に任せる
    threading.Thread(target=generate_ai_response, args=(user_input,), daemon=True).start()

def generate_ai_response(user_input):
    chat_history.append({'role': 'user', 'content': user_input})
    update_chat_area("ギャル: ")
    
    stream = ollama.chat(model=MODEL_NAME, messages=chat_history, stream=True)
    
    full_text = ""
    sentence_buffer = ""
    
    for chunk in stream:
        content = chunk['message']['content']
        update_chat_area(content) # 1文字ずつ画面に表示していく
        full_text += content
        sentence_buffer += content
        
        if any(p in content for p in ['。', '！', '？', '!', '?', '\n', '〜', '♪', 'w']):
            play_voice(sentence_buffer)
            sentence_buffer = ""
            
    if sentence_buffer.strip():
        play_voice(sentence_buffer)
        
    update_chat_area("\n\n")
    chat_history.append({'role': 'assistant', 'content': full_text})

def update_chat_area(text):
    # 画面のテキストボックスに文字を追加して、一番下まで自動スクロール
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, text)
    chat_area.see(tk.END)
    chat_area.config(state=tk.DISABLED)

# --- ここから画面（ウィンドウ）のレイアウト ---
root = tk.Tk()
root.title("Desktop Mate (Shisa Gal)")
root.geometry("400x500") # ウィンドウのサイズ
root.attributes("-topmost", True) # 常に最前面

# ★修正：先に入力欄の箱を作って、画面の「一番下（BOTTOM）」に固定する
input_frame = tk.Frame(root)
input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

# 入力欄
entry_box = tk.Entry(input_frame, font=("メイリオ", 12))
entry_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
entry_box.bind("<Return>", send_message) # Enterキー対応

# 送信ボタン
send_button = tk.Button(input_frame, text="送信", command=send_message)
send_button.pack(side=tk.RIGHT)

# ★修正：チャットエリアを後から配置して、上の「残りのスペース全部」を使わせる
chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED, font=("メイリオ", 10))
chat_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))

# アプリを起動して待機！
root.mainloop()