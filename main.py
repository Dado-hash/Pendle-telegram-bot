import requests
import time
import json
import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot
from datetime import datetime

# Load environment variables
load_dotenv()

# Telegram configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Initialize Telegram bot
bot = Bot(token=TELEGRAM_TOKEN)

# Supported chain IDs
CHAINS_TO_MONITOR = {
    1: "Ethereum",
    42161: "Arbitrum",
    10: "Optimism",
    56: "BSC",
    146: "Sonic",
    8453: "Base",
    5000: "Mantle"
}

# Base URL for Pendle API
PENDLE_API_BASE_URL = "https://api-v2.pendle.finance/core/v1"

# General notification threshold
NOTIFICATION_THRESHOLD = 20.0  # 20%

# Specific pools or PTs to be constantly monitored
specific_pools_to_track = {
    # "chain_id-address": {"min_threshold": 20.0, "name": "Descriptive name", "chain": "Chain Name"}
}

def fetch_pendle_data(chain_id):
    """Fetch active pool and Principal Token (PT) data from Pendle for a specific chain.

    Args:
        chain_id (int): The ID of the chain to fetch data from.

    Returns:
        dict or None: The chain's data if the request is successful, otherwise None.
    """
    try:
        url = f"{PENDLE_API_BASE_URL}/{chain_id}/markets/active"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error while fetching data from Pendle for chain {chain_id}: {e}")
        return None

def fetch_all_chains_data():
    """Fetch data for all configured chains.

    Returns:
        dict: A dictionary containing data for all monitored chains.
    """
    all_chain_data = {}
    for chain_id in CHAINS_TO_MONITOR.keys():
        chain_data = fetch_pendle_data(chain_id)
        if chain_data:
            all_chain_data[chain_id] = chain_data
    return all_chain_data

def analyze_apy_data(all_chain_data):
    """Analyze implied APY data from all chains and send appropriate notifications.

    Args:
        all_chain_data (dict): Dictionary containing market data per chain.
    """
    if not all_chain_data:
        return
    
    # List for notifications of pools above the general threshold
    high_apy_notifications = []
    
    # List for notifications of specific pools below their threshold
    specific_pool_notifications = []
    
    # Analyze all pools and PTs across all chains
    for chain_id, data in all_chain_data.items():
        chain_name = CHAINS_TO_MONITOR[chain_id]
        
        for market in data.get("markets", []):
            market_address = market.get("address")
            market_name = market.get("name", "Unknown")
            pool_id = f"{chain_id}-{market_address}"
            
            # Get implied APY from details and convert to percentage
            implied_apy = market.get("details", {}).get("impliedApy", 0) * 100
            
            # Check pools above the general threshold
            if implied_apy > NOTIFICATION_THRESHOLD:
                high_apy_notifications.append(
                    f"🚀 [{chain_name}] Pool {market_name} has an implied APY of {implied_apy:.2f}%"
                )
            
            # Check specific pools below their threshold
            if pool_id in specific_pools_to_track:
                pool_info = specific_pools_to_track[pool_id]
                if implied_apy < pool_info["min_threshold"]:
                    specific_pool_notifications.append(
                        f"⚠️ [{chain_name}] Your monitored pool {pool_info['name']} has dropped to {implied_apy:.2f}% (below {pool_info['min_threshold']}%)"
                    )
    
    # Send notifications
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if high_apy_notifications:
        message = f"🔔 {timestamp} - Pools with implied APY above {NOTIFICATION_THRESHOLD}%:\n\n" + "\n".join(high_apy_notifications)
        send_telegram_notification(message)
    
    if specific_pool_notifications:
        message = f"🔔 {timestamp} - Monitored pool updates:\n\n" + "\n".join(specific_pool_notifications)
        send_telegram_notification(message)

def send_telegram_notification(message):
    """Send a notification via Telegram.

    Args:
        message (str): The message to send.
    """
    try:
        asyncio.run(bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="HTML"))
        print(f"Notification sent: {message}")
    except Exception as e:
        print(f"Error while sending Telegram notification: {e}")

def add_specific_pool(chain_id, address, name, min_threshold=20.0):
    """Add a specific pool to monitor.

    Args:
        chain_id (int): The chain ID of the pool.
        address (str): The address of the pool.
        name (str): The descriptive name of the pool.
        min_threshold (float): The minimum threshold for notifications.
    """
    pool_id = f"{chain_id}-{address}"
    chain_name = CHAINS_TO_MONITOR.get(chain_id, f"Chain {chain_id}")
    
    specific_pools_to_track[pool_id] = {
        "name": name,
        "min_threshold": min_threshold,
        "chain": chain_name
    }
    print(f"Pool {name} on {chain_name} added to monitoring with minimum threshold {min_threshold}%")
    save_tracked_pools()

def remove_specific_pool(chain_id, address):
    """Remove a specific pool from monitoring.

    Args:
        chain_id (int): The chain ID of the pool.
        address (str): The address of the pool.
    """
    pool_id = f"{chain_id}-{address}"
    if pool_id in specific_pools_to_track:
        pool_name = specific_pools_to_track[pool_id]["name"]
        chain_name = specific_pools_to_track[pool_id]["chain"]
        del specific_pools_to_track[pool_id]
        print(f"Pool {pool_name} on {chain_name} removed from monitoring")
        save_tracked_pools()
    else:
        print(f"Pool with ID {pool_id} not found in monitoring")

def save_tracked_pools():
    """Save monitored pools to a JSON file."""
    with open("tracked_pools.json", "w") as f:
        json.dump(specific_pools_to_track, f)
    print("Monitored pools saved successfully")

def load_tracked_pools():
    """Load monitored pools from a JSON file."""
    global specific_pools_to_track
    try:
        with open("tracked_pools.json", "r") as f:
            specific_pools_to_track = json.load(f)
        print(f"Loaded {len(specific_pools_to_track)} monitored pools")
    except FileNotFoundError:
        print("No monitored pools found")

def add_chain_to_monitor(chain_id, chain_name):
    """Add a new chain to monitor.

    Args:
        chain_id (int): The ID of the chain to add.
        chain_name (str): The name of the chain to add.
    """
    CHAINS_TO_MONITOR[chain_id] = chain_name
    print(f"Chain {chain_name} (ID: {chain_id}) added to monitoring")

def remove_chain_from_monitor(chain_id):
    """Remove a chain from monitoring.

    Args:
        chain_id (int): The ID of the chain to remove.
    """
    if chain_id in CHAINS_TO_MONITOR:
        chain_name = CHAINS_TO_MONITOR[chain_id]
        del CHAINS_TO_MONITOR[chain_id]
        print(f"Chain {chain_name} (ID: {chain_id}) removed from monitoring")
    else:
        print(f"Chain with ID {chain_id} not found in monitoring")

def display_available_pools():
    """Display all available pools to assist in selection."""
    for chain_id, chain_name in CHAINS_TO_MONITOR.items():
        data = fetch_pendle_data(chain_id)
        if not data:
            continue
        
        print(f"\n=== AVAILABLE POOLS ON {chain_name.upper()} (Chain ID: {chain_id}) ===")
        for market in data.get("markets", []):
            implied_apy = market.get("details", {}).get("impliedApy", 0) * 100
            print(f"Name: {market.get('name', 'Unknown')}")
            print(f"Address: {market.get('address')}")
            print(f"Current implied APY: {implied_apy:.2f}%")
            print(f"Expiry: {market.get('expiry')}")
            print("-" * 40)

def main():
    print("Pendle multi-chain implied APY monitoring bot started!")
    print(f"Monitored chains: {', '.join([f'{name} (ID: {id})' for id, name in CHAINS_TO_MONITOR.items()])}")
    print("Press Ctrl+C to terminate.")
    
    # Load saved monitored pools
    load_tracked_pools()
    
    # Example: add a specific pool to monitor
    # add_specific_pool(1, "0xc374f7ec85f8c7de3207a10bb1978ba104bda3b2", "stETH", 3.0)
    
    try:
        while True:
            all_chain_data = fetch_all_chains_data()
            analyze_apy_data(all_chain_data)
            
            # Wait 10 minutes before checking again
            print(f"Waiting... Next check in 10 minutes ({time.strftime('%H:%M:%S')})")
            time.sleep(600) 
    except KeyboardInterrupt:
        print("\nBot terminated.")

if __name__ == "__main__":
    # Uncomment to display available pools when needed
    # display_available_pools()
    main()