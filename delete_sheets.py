import sys
import requests

# 1. Capture the email parameter passed from the Django command line caller
target_email = sys.argv[1].strip()

try:
    # 2. EXACT URL AND FORMAT FROM YOUR SUCCESSFUL TERMINAL COMMAND
    macro_url = 'https://script.google.com/macros/s/AKfycbwmyfF3AoJ0hDTlrPj4QUPqnpJAJGJ__x0zqtHgbFR25EfCjsW3SOzpSBizVDtq2SMnaA/exec'
    payload = {'email': target_email}
    
    # 3. Fire the secure web request to Google's macro server engine
    res = requests.post(macro_url, json=payload, timeout=15)
    
    # 4. Logs out response verification strings straight to your server console window
    print(f"📡 Google Response Status: {res.status_code}")
    print(f"📋 API Return Message: {res.text}")

except Exception as e:
    print(f"❌ Background process network execution failed: {str(e)}")
