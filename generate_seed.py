#!/usr/bin/env python3
"""
Simple script to generate a BIP-39 mnemonic seed phrase
One-time use script for creating deterministic wallets
"""

from mnemonic import Mnemonic
import argparse

def generate_seed_phrase(strength=256, language="english", passphrase=""):
    """
    Generate a BIP-39 mnemonic seed phrase
    
    Args:
        strength (int): Entropy strength in bits (128, 160, 192, 224, 256)
        language (str): Language for the wordlist
        passphrase (str): Optional passphrase for additional security
    
    Returns:
        tuple: (words, seed_hex)
    """
    # Initialize mnemonic with specified language
    mnemo = Mnemonic(language)
    
    # Generate the word list
    words = mnemo.generate(strength=strength)
    
    # Convert to seed
    seed = mnemo.to_seed(words, passphrase=passphrase)
    
    return words, seed.hex()

def main():
    parser = argparse.ArgumentParser(description="Generate BIP-39 mnemonic seed phrase")
    parser.add_argument("--strength", type=int, default=256, 
                       choices=[128, 160, 192, 224, 256],
                       help="Entropy strength in bits (default: 256)")
    parser.add_argument("--language", type=str, default="english",
                       choices=["english", "chinese_simplified", "chinese_traditional", 
                               "french", "italian", "japanese", "korean", "spanish", 
                               "turkish", "czech", "portuguese"],
                       help="Language for wordlist (default: english)")
    parser.add_argument("--passphrase", type=str, default="",
                       help="Optional passphrase for additional security")
    parser.add_argument("--show-seed", action="store_true",
                       help="Show the hex seed (be careful with this)")
    
    args = parser.parse_args()
    
    print(f"Generating {args.strength}-bit mnemonic in {args.language}...")
    print("-" * 50)
    
    try:
        words, seed_hex = generate_seed_phrase(
            strength=args.strength,
            language=args.language,
            passphrase=args.passphrase
        )
        
        print("🔐 MNEMONIC PHRASE:")
        print("=" * 50)
        print(words)
        print("=" * 50)
        
        if args.passphrase:
            print(f"\n🔑 PASSPHRASE: {args.passphrase}")
        
        if args.show_seed:
            print(f"\n🌱 SEED (HEX):")
            print("=" * 50)
            print(seed_hex)
            print("=" * 50)
        
        print(f"\n📝 WORD COUNT: {len(words.split())}")
        print(f"🔒 ENTROPY: {args.strength} bits")
        
        print("\n⚠️  SECURITY WARNINGS:")
        print("- Keep your mnemonic phrase secure and private")
        print("- Never share it with anyone")
        print("- Store it in a safe location")
        print("- Consider using a hardware wallet for large amounts")
        
    except Exception as e:
        print(f"❌ Error generating seed phrase: {e}")

if __name__ == "__main__":
    main() 