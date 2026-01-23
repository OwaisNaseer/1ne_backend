#!/usr/bin/env python
"""Verify chatbots were created successfully."""
from app.db.session import SessionLocal
from app.domains.chatbots.models import Chatbot, ChatbotCapability

db = SessionLocal()
try:
    # Check for our new chatbots
    bots = db.query(Chatbot).filter(
        Chatbot.slug.in_(['grammar-writing-mentor', 'literature-analysis-expert'])
    ).all()
    
    print(f"\n{'='*60}")
    print(f"Found {len(bots)} chatbots:")
    print(f"{'='*60}\n")
    
    for bot in bots:
        print(f"[OK] {bot.slug}")
        print(f"  Name: {bot.name}")
        print(f"  Access Level: {bot.access_level}")
        
        # Count capabilities
        caps = db.query(ChatbotCapability).filter(
            ChatbotCapability.chatbot_id == bot.id,
            ChatbotCapability.is_active == True
        ).all()
        print(f"  Capabilities: {len(caps)}")
        for cap in caps:
            print(f"    - {cap.capability_key} ({cap.capability_name})")
        print()
    
    if len(bots) == 2:
        print("[SUCCESS] Both chatbots created successfully!")
    else:
        print(f"[WARNING] Expected 2 chatbots, found {len(bots)}")
        
finally:
    db.close()
