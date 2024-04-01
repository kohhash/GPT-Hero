from requests import sessions
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Access environment variables
ZERO_API_KEY = os.getenv('ZERO_API_KEY')

def copyleaks_detector(text):
    s = sessions.Session()
    s.get("https://copyleaks.com/ai-content-detector")
    ai_detected = False
    try:
       r = s.post("https://app.copyleaks.com/api/v2/dashboard/anonymous/ai-scan/submit/text", json={
           "acdiToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhbm9ueW1vdXMtdXNlci1pcCI6IjI2MDM6ODA4MDoyMTAwOmVjMDoyNGJkOjEzZjQ6OTFmZDphMzE0IiwibmJmIjoxNjgwMTQ5NjY5LCJleHAiOjE2ODAxNjA0NjksImlhdCI6MTY4MDE0OTY2OSwiaXNzIjoiaHR0cHM6Ly9hcHAuY29weWxlYWtzLmNvbS8iLCJhdWQiOiJhaS1jb250ZW50LWRldGVjdG9yLWlmcmFtZSJ9.3DuQEJ3EhvDlDH1dTCCeMeNVlKeG4eaNSw40xxemjRQ",
        "text": text,
        "sim": 1})
       if r.json()['summary']['ai'] > 0.5:
            ai_detected = True
    except Exception as e:
        print("Error occured")
    return ai_detected



def gptzero_detector(text):
    creds = {"email":"dueltmp+d9zvn@gmail.com","password":"dueltmp+d9zvn@gmail.com","gotrue_meta_security":{}}
    detected=False
    try:
        s = sessions.Session()
        s.get("https://gptzero.me/")
        headers = {
            "apikey": ZERO_API_KEY,
            "Origin": "https://app.gptzero.me",
            "Referer": "https://app.gptzero.me",
            "Sec - Fetch - Site": "cross - site",
            "Sec - Fetch - Mode": "cors",
            "Sec - Fetch - Dest": "empty",
            "Authorization": "Bearer " + ZERO_API_KEY

        }
        r = s.post("https://lydqhgdzhvsqlcobdfxi.supabase.co/auth/v1/token?grant_type=password", json=creds,headers=headers)
        access_token = r.json()['access_token']

        headers = {
            # ":authority:": "api.gptzero.me",
            "content-type": "application/json",
            "Origin": "https://app.gptzero.me",
            "Referer": "https://app.gptzero.me",
            "cookie": f"AMP_MKTG=JTdCJTIycmVmZXJyZXIlMjIlM0ElMjJodHRwcyUzQSUyRiUyRmFwcC5ncHR6ZXJvLm1lJTJGbG9naW4lMjIlMkMlMjJyZWZlcnJpbmdfZG9tYWluJTIyJTNBJTIyYXBwLmdwdHplcm8ubWUlMjIlN0Q=; AMP=JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjJlM2E0ZGEwOC00MzZjLTRjNDEtYjA1NS0xNmQ2NTY0ZjY0NzUlMjIlMkMlMjJzZXNzaW9uSWQlMjIlM0ExNjc4MDY3ODMxMDYyJTJDJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJsYXN0RXZlbnRUaW1lJTIyJTNBMTY3ODA3MDExODExOSU3RA==; AMP_MKTG_8f1ede8e9c=JTdCJTIycmVmZXJyZXIlMjIlM0ElMjJodHRwcyUzQSUyRiUyRnd3dy5nb29nbGUuY29tJTJGJTIyJTJDJTIycmVmZXJyaW5nX2RvbWFpbiUyMiUzQSUyMnd3dy5nb29nbGUuY29tJTIyJTdE; 	accessToken={access_token}; AMP_8f1ede8e9c=JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjI1ZGNlYjY3OS00NmNjLTRmNDMtYTdiMS03YTMwZWZkY2IyNDglMjIlMkMlMjJzZXNzaW9uSWQlMjIlM0ExNjc5NTY5OTcwNTk5JTJDJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJsYXN0RXZlbnRUaW1lJTIyJTNBMTY3OTU3MTg2NDcxMyU3RA=="
        }

        r = s.post("https://api.gptzero.me/v2/predict/text", json={"document":text}, headers=headers)
        detected = r.json()['documents'][0]['average_generated_prob'] >= 0.5
    except Exception as e:
        print(e)
    return detected