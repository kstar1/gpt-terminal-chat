# query_gpt.py
import openai
import os
from dotenv import load_dotenv
import time
import argparse
import shutil
import glob
import datetime

# Load the API key
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Helper Functions ===

def chat_with_gpt(messages, model="gpt-4o", temperature=0.5, max_tokens=500, stream=False):
    return client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=stream
    )

def save_chat_log(chat_log, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(chat_log)

def log_token_usage(model, usage_total_tokens):
    with open("token_usage.log", "a", encoding="utf-8") as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] Model: {model} | Tokens used: {usage_total_tokens}\n")

def auto_summarize_chat(messages, model="gpt-4o"):
    summarize_prompt = (
        "Please summarize this conversation between the user and assistant "
        "in a concise, clear manner. Focus on main topics discussed."
    )
    summary_messages = messages + [{"role": "user", "content": summarize_prompt}]
    try:
        response = client.chat.completions.create(
            model=model,
            messages=summary_messages,
            temperature=0.3,
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"⚠️ Could not generate summary: {e}")
        return None

def auto_generate_title(messages, model="gpt-4o"):
    title_prompt = (
        "Based on this conversation, suggest a short 3-5 word title that would best describe it. "
        "Return ONLY the title text without quotation marks or any prefix."
    )
    title_messages = messages + [{"role": "user", "content": title_prompt}]
    try:
        response = client.chat.completions.create(
            model=model,
            messages=title_messages,
            temperature=0.5,
            max_tokens=20
        )
        return response.choices[0].message.content.strip().replace(" ", "_")
    except Exception as e:
        print(f"⚠️ Could not generate title: {e}")
        return f"chat_{time.strftime('%Y%m%d-%H%M%S')}"

def load_history_from_file(file_path):
    loaded_messages = []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if line.startswith("[") and "] You:" in line:
            content = line.split("] You:")[-1].strip()
            loaded_messages.append({"role": "user", "content": content})
        elif line.startswith("[") and "] Assistant:" in line:
            content = line.split("] Assistant:")[-1].strip()
            loaded_messages.append({"role": "assistant", "content": content})
    return loaded_messages

def get_timestamp():
    return time.strftime("[%H:%M:%S]")

# === Main Script ===

if __name__ == "__main__":
    print("🌟 Welcome to your GPT Terminal Chat 🌟")

    # Markdown Output First
    markdown_choice = input("Do you want Markdown output for VS Code? (y/n): ").lower()
    markdown_output = markdown_choice == "y"

    # Load Previous Chats if wanted
    messages = []
    history_choice = input("Do you want to load previous chats? (y/n): ").lower()
    if history_choice == "y":
        files = glob.glob("chats/chat_*.md") + glob.glob("chats/chat_*.txt")
        if files:
            print("\nAvailable chat files:")
            for idx, file in enumerate(files):
                print(f"{idx+1}. {file}")

            file_indexes = input("\nEnter file numbers to load, separated by commas (e.g., 1,3): ").split(",")
            for idx in file_indexes:
                idx = int(idx.strip()) - 1
                messages += load_history_from_file(files[idx])
            print(f"✅ Loaded {len(file_indexes)} chat(s) into current session.")
        else:
            print("⚠️ No chat logs found. Starting fresh.")

    # Then Model Choice
    model = input("\nWhich model do you want to use? (default gpt-4o): ") or "gpt-4o"

    chat_log = ""
    timestamp_now = time.strftime("%Y%m%d-%H%M%S")
    temp_log_filename = f"temp_chat_log_{timestamp_now}.txt"
    os.makedirs("chats", exist_ok=True)

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in {"exit", "quit"}:
            print("\n👋 Exiting chat...")
            break

        messages.append({"role": "user", "content": user_input})
        print("\nAssistant: ", end="", flush=True)

        # Stream response
        stream_response = chat_with_gpt(messages, model=model, stream=True)
        full_response = ""

        for chunk in stream_response:
            if chunk.choices[0].delta.content:
                chunk_text = chunk.choices[0].delta.content
                print(chunk_text, end="", flush=True)
                full_response += chunk_text

        if markdown_output:
            formatted_response = f"\n\n```\n{full_response}\n```\n"
        else:
            formatted_response = full_response

        chat_log += f"\n{get_timestamp()} You: {user_input}\n{get_timestamp()} Assistant: {formatted_response}\n"
        messages.append({"role": "assistant", "content": full_response})

        # Log token usage (based on full non-stream response)
        non_stream_response = chat_with_gpt(messages, model=model, stream=False)
        total_tokens = non_stream_response.usage.total_tokens
        log_token_usage(model, total_tokens)

    # After exit - ask if want to save
    should_save = input("\n📝 Do you want to save this chat? (y/n): ").lower()

    if should_save == "y":
        # Auto generate a title
        print("\n🔖 Generating an apt chat title...")
        apt_name = auto_generate_title(messages, model=model)
        extension = "md" if markdown_output else "txt"
        final_log_filename = f"chats/chat_{apt_name}_{timestamp_now}.{extension}"

        # Save chat
        save_chat_log(chat_log, filename=temp_log_filename)

        # Summarize
        print("\n🧹 Summarizing the chat...")
        summary = auto_summarize_chat(messages, model=model)
        if summary:
            with open(temp_log_filename, "a", encoding="utf-8") as f:
                f.write("\n\n--- Chat Summary ---\n")
                f.write(summary)

        shutil.move(temp_log_filename, final_log_filename)
        print(f"✅ Chat saved as {final_log_filename}")

    else:
        if os.path.exists(temp_log_filename):
            os.remove(temp_log_filename)
        print("🗑️ Chat discarded. Nothing saved.")
