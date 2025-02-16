import subprocess
import time
import os
import signal
import sys

def start_services():
    # Start Flask app
    print("Starting Flask app...")
    flask_process = subprocess.Popen(['python3', 'app.py'])
    
    # Give Flask more time to start - increased from 3 to 10 seconds
    print("Waiting for Flask to initialize...")
    time.sleep(10)
    
    # Configure ngrok
    print("Configuring ngrok...")
    auth_process = subprocess.run(['./ngrok', 'authtoken', os.getenv('NGROK_AUTH_TOKEN')],  
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE)
    
    # Start ngrok
    print("Starting ngrok...")
    ngrok_process = subprocess.Popen(['./ngrok', 'http', '5000'], stdout=subprocess.PIPE)
    
    # Give ngrok time to establish tunnel
    time.sleep(5)
    
    # Verify Flask is responding
    try:
        subprocess.check_output(['curl', '-s', 'http://localhost:5000'])
        print("✅ Flask server is running")
    except:
        print("⚠️ Warning: Flask server may not be running properly")
    
    # Get ngrok URL
    try:
        tunnel_url = subprocess.check_output(['curl', '-s', 'http://localhost:4040/api/tunnels'])
        import json
        url = json.loads(tunnel_url)['tunnels'][0]['public_url']
        print(f"\n🌐 Your Flatland Explorer is live at: {url}")
        print("Share this URL with others!")
        print("\n⚠️ This URL will work for about 8 hours")
        print("Press Ctrl+C to stop the server")
    except Exception as e:
        print("\n⚠️ Server is running but couldn't get the URL automatically.")
        print("Please check http://localhost:4040 in your browser to find the URL")
        print(f"Error details: {str(e)}")
    
    return flask_process, ngrok_process

def cleanup(flask_process, ngrok_process):
    print("\n\nShutting down services...")
    flask_process.terminate()
    ngrok_process.terminate()
    sys.exit(0)

if __name__ == "__main__":
    try:
        flask_process, ngrok_process = start_services()
        # Keep script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup(flask_process, ngrok_process)