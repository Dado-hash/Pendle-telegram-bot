# 🚀 Pendle APY Telegram Bot

This Python bot monitors Pendle Finance markets across multiple chains and sends real-time alerts via Telegram when:

- A pool's implied APY exceeds a general threshold (default: **20%**)
- A specific pool you're tracking drops below a custom APY threshold

## 🛡️ How it Works

The bot queries [Pendle's v2 API](https://api-v2.pendle.finance/core/v1) every 10 minutes and analyzes the APY of each pool across selected chains. When thresholds are breached, it sends a Telegram message to a specified chat.

---

## 🧹 Features

- ✅ Multi-chain support (Ethereum, Arbitrum, Optimism, BSC, Mantle, Base, Sonic...)
- 🔔 Telegram notifications for:
  - Pools above general APY threshold
  - Custom tracked pools that fall below their personal threshold
- 📂 Automatic tracking persistence using `tracked_pools.json`
- 🧪 Easily extendable to support new chains or pools

---

## 🛠️ Installation

Clone the repo and install dependencies:

```bash
git clone https://github.com/yourusername/pendle-telegram-bot.git
cd pendle-telegram-bot
python3 -m venv pendle_bot_env
source pendle_bot_env/bin/activate
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Create a `.env` file in the project root and add:

```env
TELEGRAM_TOKEN=your_telegram_bot_token
CHAT_ID=your_telegram_chat_id
```

To find your `CHAT_ID`, you can send a message to your bot and use tools like [getIDs bot](https://t.me/getmyid_bot) or log the update payload.

---

## 🚀 Running the Bot

Simply start the bot:

```bash
python main.py
```

It will:

- Load tracked pools from `tracked_pools.json`
- Begin checking APYs every 10 minutes
- Send alerts if thresholds are triggered

You can press `Ctrl+C` to stop the bot.

---

## ➕ Adding or Removing Specific Pools

You can add a specific pool for more granular tracking directly in `main.py`, e.g.:

```python
add_specific_pool(
    1,
    "0xc374f7ec85f8c7de3207a10bb1978ba104bda3b2",
    "stETH Pendle Pool",
    min_threshold=5.0
)
```

---

## 📝 Customizing

### Add or remove chains

Edit the `CHAINS_TO_MONITOR` dictionary in `main.py` to include new chain IDs and names.

### Change the general APY threshold

Change the `NOTIFICATION_THRESHOLD` variable to your desired percentage.

---

## 🛆 Dependencies

- [`requests`](https://pypi.org/project/requests/)
- [`python-dotenv`](https://pypi.org/project/python-dotenv/)
- [`python-telegram-bot`](https://pypi.org/project/python-telegram-bot/)

---

## 🧐 Author

Made with ❤️ by **Davide**

---

## 📜 License

This project is licensed under the MIT License.

