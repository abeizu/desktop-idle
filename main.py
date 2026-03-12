import ollama

def chat_with_ai(user_input):
    print(f"\nあなた: {user_input}")
    print("AI: ", end="", flush=True)
    
    # Ollama経由でQwen2.5にメッセージを送信（ストリーミング出力）
    stream = ollama.chat(
        model='qwen2.5',
        messages=[{'role': 'user', 'content': user_input}],
        stream=True
    )
    
    # 返答を1文字ずつリアルタイムで表示
    for chunk in stream:
        print(chunk['message']['content'], end='', flush=True)
    print("\n")

if __name__ == "__main__":
    print("AIが起動しました。（終了するには 'exit' と入力）")
    while True:
        user_text = input("> ")
        if user_text.lower() == 'exit':
            break
        chat_with_ai(user_text)