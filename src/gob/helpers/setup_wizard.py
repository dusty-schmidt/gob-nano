"""Setup wizards for Gob configuration"""

import os
import webbrowser


def run_discord_wizard() -> str:
    """Interactive Discord bot setup wizard"""
    print("\n" + "="*60)
    print("🎮 Discord Bot Setup (Optional)")
    print("="*60)
    print()
    print("Want Gob always listening in Discord?")
    print()
    
    response = input("Set up Discord bot now? (y/n): ").strip().lower()
    if response != 'y':
        print("\n⏭️  Skipping Discord setup for now")
        print("You can set it up later by running: ./gob.sh\n")
        return ""
    
    print()
    print("📋 Follow these steps to get your Discord token:\n")
    print("1. Go to Discord Developer Portal")
    print("   → https://discord.com/developers/applications")
    
    open_portal = input("Open Discord Developer Portal now? (y/n): ").strip().lower()
    if open_portal == 'y':
        try:
            webbrowser.open('https://discord.com/developers/applications')
            print("✅ Opening in browser...\n")
        except:
            pass
    
    print("2. Click 'New Application' → Enter name: 'Gob Agent'")
    input("   Press Enter when created...")
    print()
    print("3. Go to 'Bot' section → Click 'Add Bot'")
    input("   Press Enter when bot is added...")
    print()
    print("4. Under TOKEN, click 'Copy'")
    print("   ⚠️  NEVER share this token publicly!")
    
    token = input("\nPaste your Discord bot token: ").strip()
    if not token or len(token) < 50:
        print("❌ Invalid token")
        return run_discord_wizard()
    
    print()
    print("5. Go to 'OAuth2' → 'URL Generator'")
    print("   Scopes: bot | Permissions: Send Messages, Read History")
    print("   Copy URL and add bot to your server")
    
    input("Press Enter when done...")
    print("\n✅ Discord bot setup complete!")
    return token


def run_api_key_wizard() -> str:
    """Interactive OpenRouter API key setup"""
    print("\n" + "="*60)
    print("🔑 OpenRouter API Key Setup")
    print("="*60)
    print()
    print("1. Go to OpenRouter Dashboard")
    print("   → https://openrouter.ai/keys")
    
    open_portal = input("Open OpenRouter in browser? (y/n): ").strip().lower()
    if open_portal == 'y':
        try:
            webbrowser.open('https://openrouter.ai/keys')
            print("✅ Opening in browser...\n")
        except:
            pass
    
    print("2. Create or copy your API key")
    print()
    
    api_key = input("Paste your OpenRouter API key: ").strip()
    if not api_key or len(api_key) < 20:
        print("❌ Invalid API key")
        return run_api_key_wizard()
    
    # Save to .env in project root
    from pathlib import Path
    env_path = Path.cwd().parent.parent.parent / '.env'
    
    with open(env_path, 'a') as f:
        f.write(f"\nOPENROUTER_API_KEY={api_key}\n")
    
    os.environ['OPENROUTER_API_KEY'] = api_key
    
    print(f"\n✅ API key saved to .env")
    return api_key
