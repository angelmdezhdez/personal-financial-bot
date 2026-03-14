# 🤖 Personal Financial Bot

## 📖 Overview

The **Personal Financial Bot** is a Telegram bot designed to help users track and manage their personal finances directly from their chat application. It provides a simple and intuitive way to record income and expenses, view current balances, and retrieve transaction history, all through a conversational interface. This bot aims to simplify personal money management by bringing it into a platform you already use daily.

## ✨ Features

*   **📈 Expense Tracking:** Easily record your daily expenses with simple commands.
*   **💰 Income Logging:** Log your income to keep a clear overview of your earnings.
*   **📊 Current Balance:** Instantly check your available balance.
*   **📜 Transaction History:** View a chronological list of your past financial transactions.
*   **👤 User-Specific Data:** Each user's financial data is managed independently and securely.
*   **💾 Persistent Storage:** All financial data is stored locally using SQLite, ensuring your records are safe.

## 🛠️ Tech Stack

**Backend & Bot Logic:**

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)

**Database:**

![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)

## 🚀 Quick Start

### Prerequisites
Before you begin, ensure you have the following installed:
- **Python 3.8+** (or newer)
- A **Telegram Bot Token** (obtainable from BotFather on Telegram)

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/angelmdezhdez/personal-financial-bot.git
    cd personal-financial-bot
    ```

2.  **Environment setup**
    Create a `.env` file in the root directory for your bot's token:
    ```bash
    cp .env.example .env # (If .env.example exists, otherwise create it manually)
    ```
    Open the newly created `.env` file and add your Telegram Bot Token:
    ```
    TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN_HERE"
    ```
    *Replace `YOUR_TELEGRAM_BOT_TOKEN_HERE` with the token you got from BotFather.*

6.  **Interact with the bot**
    Open Telegram, search for your bot by its username, and start chatting!

## 📁 Project Structure

```
personal-financial-bot/
├── .gitignore             # Standard git ignore rules for Python
├── LICENSE                # MIT License
├── README.md              # Project documentation
├── bot/                   # Contains bot-specific logic
│   ├── bot.py             # bot construction
│   └── tools.py           # tools for the agent
├── data/                  # Directory for persistent data
│   └── finance.db         # SQLite database file for financial records
├── main.py                # Main application entry point, bot initialization
└── utils/                 # Utility functions and modules
    └── requirements.txt   # requierements for running
```

---

<div align="center">

**⭐ Star this repo if you find it helpful!**

Made with ❤️ by [angelmdezhdez](https://github.com/angelmdezhdez)

</div>
```