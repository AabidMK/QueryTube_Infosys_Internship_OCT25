# test_ollama.py
import requests
import json

def test_ollama():
    try:
        print("🔍 Testing Ollama connection...")
        response = requests.get('http://localhost:11434/api/tags', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f"✅ Ollama is running! Found {len(models)} models")
            
            if models:
                print("\n📋 Available models:")
                for model in models:
                    print(f"   - {model['name']}")
            else:
                print("ℹ️  No models installed yet.")
                
            return True
        else:
            print(f"❌ Ollama returned status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama. Make sure:")
        print("   1. Ollama is installed from https://ollama.ai")
        print("   2. Ollama is running (check system tray)")
        print("   3. Try running 'ollama serve' in terminal")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_ollama()