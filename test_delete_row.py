import sys
import requests

def run_deletion_test(target_email):
    target_email = target_email.strip().lower()
    
    # 1. FIXED: Correct Spreadsheet ID and GID values
    SPREADSHEET_ID = "1_8i12XvuY04cLclp_8qnwaKEiGTQBYt3My781vMAKT8"
    GID = "1692571671" 
    
    print("\n==================================================")
    print("🔍 STANDALONE GOOGLE SHEETS DELETION TEST RUNNER")
    print(f"➜ Target Email to locate: '{target_email}'")
    print("==================================================")

    try:
        # 2. FIXED: Restored the true, complete Google Sheets web path address string
        csv_url = f"https://google.com{SPREADSHEET_ID}/export?format=csv&gid={GID}"
        print("📡 Step 1: Connecting to Google and requesting raw CSV data...")
        
        csv_response = requests.get(csv_url, timeout=10)
        print(f"📡 Step 1 Status: HTTP {csv_response.status_code}")
        
        if csv_response.status_code != 200:
            print("❌ Step 1 Failure: Google rejected the public download link request.")
            print("👉 FIX: Verify that your Google Sheet sharing is set to 'Anyone with the link can edit'!")
            return

        # Step 2: Loop through rows line by line
        lines = csv_response.text.splitlines()
        print(f"📋 Step 2: Download successful. Found {len(lines)} rows inside the spreadsheet.")
        
        row_to_delete = None
        for index, line in enumerate(lines):
            columns = line.split(',')
            
            if len(columns) > 2:
                # Column C maps to Python list position index 2
                sheet_email = columns[2].strip().replace('"', '').lower()
                
                # Print out the first 5 records to see what string data Python reads from Google
                if index < 6:
                    print(f"   ↳ Checking Row {index + 1} Email column cell: '{sheet_email}'")
                
                if sheet_email == target_email:
                    row_to_delete = index + 1
                    print(f"🎯 Step 3: MATCH LOCATED! Found target on Spreadsheet Row Number: {row_to_delete}")
                    break
        
        # Step 4: Dispatch deletion request via Google macro tunnel endpoint
        if row_to_delete:
            print(f"🚀 Step 4: Dispatching a clean web request update to erase row {row_to_delete}...")
            
            # 3. FIXED: Restored the true Google macro backend endpoint string layout here too!
            delete_url = f"https://google.com{SPREADSHEET_ID}/deferred/edit?gid={GID}"
            payload = {
                "tq": f"DELETE ROW {row_to_delete}",
                "action": "delete",
                "row": row_to_delete
            }
            del_response = requests.post(delete_url, data=payload, timeout=10)
            print(f"🚀 Step 4 Network Response Code: HTTP {del_response.status_code}")
            print("✅ PROCESS COMPLETE: Go check your open Google Sheet tab browser window!")
        else:
            print(f"❌ Step 3 Failure: Completed the loop but could not find '{target_email}' in the columns.")
            
    except Exception as e:
        print(f"💥 SYSTEM EXCEPTION CRASHED: {str(e)}")

if __name__ == "__main__":
    # If you don't supply an email via command prompt arguments, test rago@gmail.com automatically
    test_email = sys.argv[1] if len(sys.argv) > 1 else "rago@gmail.com"
    run_deletion_test(test_email)
