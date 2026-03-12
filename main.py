import ollama
import requests
import json
import winsound
import os

# VOICEVOXの設定
VOICEVOX_URL = "http://127.0.0.1:50021"
# 47は「ナースロボ＿タイプＴ（ノーマル）」のIDです
SPEAKER_ID = 47 

def play_voice(text):
    # 空白や記号だけなら音声を生成しない
    if not text.strip():
        return
        
    params = {'text': text, 'speaker': SPEAKER_ID}
    res_query = requests.post(f"{VOICEVOX_URL}/audio_query", params=params)
    
    if res_query.status_code != 200:
        return

    query_data = res_query.json()
    res_synth = requests.post(
        f"{VOICEVOX_URL}/synthesis",
        params={'speaker': SPEAKER_ID},
        data=json.dumps(query_data),
        headers={'Content-Type': 'application/json'}
    )
    
    wav_filename = "temp_voice.wav"
    with open(wav_filename, "wb") as f:
        f.write(res_synth.content)
    
    # 音声を再生（プログラムは再生が終わるまでここで少し待機します）
    winsound.PlaySound(wav_filename, winsound.SND_FILENAME)
    
    if os.path.exists(wav_filename):
        os.remove(wav_filename)

def chat_with_ai(user_input):
    print(f"\nあなた: {user_input}")
    print("AI: ", end="", flush=True)
    
    stream = ollama.chat(
        model='qwen2.5',
        messages=[{'role': 'user', 'content': user_input}],
        stream=True
    )
    
    # 1文ずつ貯めるためのバッファ（箱）
    sentence_buffer = ""
    
    for chunk in stream:
        content = chunk['message']['content']
        print(content, end='', flush=True)
        sentence_buffer += content
        
        # 「。！？\n」のどれかが来たら、そこまでの文章を音声にして再生する
        if any(p in content for p in ['。', '！', '？', '!', '?', '\n']):
            play_voice(sentence_buffer)
            sentence_buffer = "" # 喋り終わったら箱を空にする
            
    # 最後に「。」などで終わらなかった文章が残っていれば再生する
    if sentence_buffer.strip():
        play_voice(sentence_buffer)
        
    print("\n")

if __name__ == "__main__":
    print("AIが起動しました。（終了するには 'exit' と入力）")
    while True:
        user_text = input("> ")
        if user_text.lower() == 'exit':
            break
        chat_with_ai(user_text)