# gptchat/main.py

import openai
import os
from dotenv import load_dotenv
import time
import shutil
import glob
import datetime

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich import print as rprint

# Load the API key from .env
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

console = Console()

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
        rprint(f"[bold red]⚠️ Could not generate summary: {e}[/bold red]")
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
        rprint(f"[bold red]⚠️ Could not generate title: {e}[/bold red]")
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

# === Main Function ===

def main():
    console.rule("[bold magenta]🌟 GPT Terminal Chat 🌟", style="cyan")

    # Markdown Output Toggle
    markdown_choice = Prompt.ask("Do you want [cyan]Markdown output[/cyan] for VS Code?", choices=["y", "n"])
    markdown_output = markdown_choice == "y"

    # Load Previous Chat History
    messages = []
    history_choice = Prompt.ask("Do you want to [green]load previous chats[/green]?", choices=["y", "n"])
    if history_choice == "y":
        files = glob.glob("chats/chat_*.md") + glob.glob("chats/chat_*.txt")
        if files:
            rprint("\n[bold yellow]Available chat files:[/bold yellow]")
            for idx, file in enumerate(files):
                rprint(f"[green]{idx+1}.[/green] {file}")

            file_indexes = Prompt.ask("\nEnter file numbers to load (e.g., 1,3)").split(",")
            for idx in file_indexes:
                idx = int(idx.strip()) - 1
                messages += load_history_from_file(files[idx])
            rprint(f"[bold green]✅ Loaded {len(file_indexes)} chat(s) into current session.[/bold green]")
        else:
            rprint("[bold red]⚠️ No chat logs found. Starting fresh.[/bold red]")

    # Model Selection
    model = Prompt.ask("Which [yellow]model[/yellow] do you want to use?", default="gpt-4o")

    chat_log = ""
    timestamp_now = time.strftime("%Y%m%d-%H%M%S")
    temp_log_filename = f"temp_chat_log_{timestamp_now}.txt"
    os.makedirs("chats", exist_ok=True)

    while True:
        user_input = Prompt.ask("[bold cyan]You[/bold cyan]")
        if user_input.lower() in {"exit", "quit"}:
            rprint("\n[bold red]👋 Exiting chat...[/bold red]")
            break

        messages.append({"role": "user", "content": user_input})
        rprint("\n[bold green]Assistant:[/bold green] ", end="")

        # Stream the assistant response
        stream_response = chat_with_gpt(messages, model=model, stream=True)
        full_response = ""

        for chunk in stream_response:
            if chunk.choices[0].delta.content:
                chunk_text = chunk.choices[0].delta.content
                console.print(chunk_text, end="", highlight=False, soft_wrap=True)
                full_response += chunk_text

        # Display assistant response inside a panel
        console.print(Panel(full_response, title="Assistant", title_align="left", style="bold green"))

        if markdown_output:
            formatted_response = f"\n\n```\n{full_response}\n```\n"
        else:
            formatted_response = full_response

        chat_log += f"\n{get_timestamp()} You: {user_input}\n{get_timestamp()} Assistant: {formatted_response}\n"
        messages.append({"role": "assistant", "content": full_response})

        # Log token usage (after full response)
        non_stream_response = chat_with_gpt(messages, model=model, stream=False)
        total_tokens = non_stream_response.usage.total_tokens
        log_token_usage(model, total_tokens)

    # After exiting chat
    should_save = Prompt.ask("\n📝 Do you want to [cyan]save this chat[/cyan]?", choices=["y", "n"])

    if should_save == "y":
        # Auto-generate a title
        rprint("\n[bold cyan]🔖 Generating an apt chat title...[/bold cyan]")
        apt_name = auto_generate_title(messages, model=model)
        extension = "md" if markdown_output else "txt"
        final_log_filename = f"chats/chat_{apt_name}_{timestamp_now}.{extension}"

        # Save chat log first
        save_chat_log(chat_log, filename=temp_log_filename)

        # Summarize and append
        rprint("\n[bold yellow]🧹 Summarizing the chat...[/bold yellow]")
        summary = auto_summarize_chat(messages, model=model)
        if summary:
            with open(temp_log_filename, "a", encoding="utf-8") as f:
                f.write("\n\n--- Chat Summary ---\n")
                f.write(summary)

        shutil.move(temp_log_filename, final_log_filename)
        rprint(f"[bold green]✅ Chat saved as {final_log_filename}[/bold green]")

    else:
        if os.path.exists(temp_log_filename):
            os.remove(temp_log_filename)
        rprint("[bold red]🗑️ Chat discarded. Nothing saved.[/bold red]")

# === CLI Entry Point ===

if __name__ == "__main__":
    main()
