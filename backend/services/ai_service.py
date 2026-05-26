import os
from datetime import datetime
from openai import OpenAI


def process_translation(novel_path, vocab_path, api_key):

    os.makedirs("outputs", exist_ok=True)

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

    # =========================
    # READ FILES
    # =========================
    with open(novel_path, "r", encoding="utf-8") as f:
        novel_text = f.read()

    with open(vocab_path, "r", encoding="utf-8") as f:
        vocab_list = [line.strip() for line in f if line.strip()]

    vocab_str = ", ".join(vocab_list)

    # =========================
    # PROMPT
    # =========================
    system_prompt = """
你是专业英文文学翻译AI。

要求：
- 中文 → 英文
- 文学性表达
- 尽量使用词汇表
- 只输出英文
"""

    user_prompt = f"""
请翻译以下中文小说：

必须使用词汇表：
{vocab_str}

内容：
{novel_text}
"""

    # =========================
    # CALL AI
    # =========================
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=2000
    )

    output_text = response.choices[0].message.content

    # =========================
    # SAVE FILE
    # =========================
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"outputs/output_{timestamp}.txt"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output_text)

    return {
        "text": output_text,
        "path": output_path
    }