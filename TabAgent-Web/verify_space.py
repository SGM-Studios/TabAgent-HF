from gradio_client import Client
import gradio_client
import os

print(f"Gradio Client Version: {gradio_client.__version__}")

token = os.getenv("HF_TOKEN")
space_url = "https://scottymills-tab-agent.hf.space/"

print(f"Connecting to {space_url}...")

try:
    # Try using headers for auth if hf_token arg fails
    client = Client(space_url, headers={"Authorization": f"Bearer {token}"})
    print("Connected!")
    
    print("\n--- API Information ---")
    client.view_api()
    
    print("\nVerification Complete")
except Exception as e:
    print(f"Connection Failed: {e}")
