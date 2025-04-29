
# GPT Terminal Chat App

🌟 A lightweight, private, and customizable ChatGPT-powered terminal application built in Python.

- Markdown or plain text output
- Persistent memory (auto loads old conversations if needed)
- Chat summarization and auto-titling
- Token usage tracking and cost estimation
- Clean colorful UI using `rich`
- Local file-based architecture (no external server)

---

## 🚀 Installation

1. Clone this repository:

```bash
git clone https://github.com/YOUR_USERNAME/gpt-terminal-chat.git
cd gpt-terminal-chat
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install the app locally:

```bash
pip install -e .
```

---

## ⚡ Setup

1. Create a `.env` file in the project root:

```plaintext
OPENAI_API_KEY=your_openai_api_key_here
```

✅ This keeps your OpenAI key secure.

---

## 🛠 How to Use

### Start Chatting:

```bash
gptchat
```

- Choose whether you want Markdown output
- Choose a model (default: `gpt-4o`)
- Chat live with colorful streaming responses
- Save your conversations as `.md` or `.txt`
- Auto-title and summarize your sessions

---

### Check Token Usage and Cost:

```bash
python cost_calculator.py
```

✅ Calculates:
- Token usage per model
- Dollar cost over the past 30 days (default)

---

## 📂 Project Structure

```plaintext
gptchat/
    __init__.py
    main.py            # Main app logic
chats/
    chat logs (*.md / *.txt)
token_usage.log        # Tracks API usage for cost
requirements.txt
setup.py               # Package installation script
pyproject.toml         # Build system file
.env                   # (local only) API key
```

---

## 💬 Notes

- This project uses OpenAI's **gpt-4o** by default but supports others (`gpt-4`, `gpt-3.5-turbo`, etc.)
- No server or cloud needed. Entirely **local**.
- Future upgrades may include bot personas, a text UI (TUI), or tabbed sessions.

---

## ⚖️ License

This is a personal project. No license applied unless specified otherwise.

---
