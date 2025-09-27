#!/usr/bin/env python3
"""
Test OpenRouter API directly to verify it's working.
"""

import os
import requests
from dotenv import load_dotenv

def test_openrouter_api():
    """Test OpenRouter API directly."""
    load_dotenv()
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    print(f'API Key configured: {bool(api_key)}')
    
    if not api_key:
        print('❌ No API key found')
        return False
        
    print(f'API Key starts with: {api_key[:15]}...')
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'meta-llama/llama-3.2-3b-instruct:free',
        'messages': [
            {
                'role': 'system', 
                'content': 'You are a helpful medical assistant. Provide specific information about medications when asked.'
            },
            {
                'role': 'user', 
                'content': 'I am taking Prednisone 20mg twice daily. What should I know about this medication?'
            }
        ],
        'max_tokens': 200
    }
    
    try:
        response = requests.post('https://openrouter.ai/api/v1/chat/completions', 
                               headers=headers, json=data, timeout=20)
        print(f'Direct API Status: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            print('✅ OpenRouter API working!')
            content = result['choices'][0]['message']['content']
            print(f'Response: {content}')
            
            # Check if response is specific about Prednisone
            if 'prednisone' in content.lower():
                print('✅ AI provides specific medication information!')
                return True
            else:
                print('❌ AI response is too generic')
                return False
        else:
            print(f'❌ API Error: {response.text}')
            return False
            
    except Exception as e:
        print(f'❌ API Test Error: {e}')
        return False

if __name__ == "__main__":
    print("🧪 Testing OpenRouter API Directly")
    print("=" * 50)
    
    if test_openrouter_api():
        print("\n✅ OpenRouter is working - the issue is in our backend integration")
    else:
        print("\n❌ OpenRouter API has issues")
