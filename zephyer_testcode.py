import requests
import json

def make_authenticated_request(api_url, bearer_token):
    print(bearer_token)
    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Content-Type': 'application/json',  # Adjust content type if needed
    }
    payload = {
        "projectKey": "SCRUM",
        "name": "Check axial pump1",
        "objective": "To ensure the axial pump can be enabled",
        "precondition": "Latest version of the axial pump available",
        "priorityName": "High",
        "statusName": "Draft",

    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        print(response.text)
        # Check if the request was successful (status code 201)
        if response.status_code == 201:
            print("Request successful. Response:")
            print(response.json())
        else:
            print(f"Error: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

# Replace 'YOUR_API_URL' with the actual API endpoint you want to access
api_url = 'https://api.zephyrscale.smartbear.com/v2/testcases'
bearer_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjb250ZXh0Ijp7ImJhc2VVcmwiOiJodHRwczovL2lpdGgtdGVhbS1xNHc2dnVyZi5hdGxhc3NpYW4ubmV0IiwidXNlciI6eyJhY2NvdW50SWQiOiI3MTIwMjA6ODYzYWQ0ZTctMDljNS00NjE1LThiZjgtZTQ3YzA3YmRkMjEzIiwidG9rZW5JZCI6IjkxMjliMjYxLTkwNTUtNDEyNi1hNzcyLTRiYWVlYTJiMDdkMiJ9fSwiaXNzIjoiY29tLnRoZWQuemVwaHlyLmplIiwic3ViIjoiZjU2NmY4YzYtODk3NS0zYTI0LTgzMzgtMTMxNzIwZjYzMTY1IiwiZXhwIjoxNzc1MzMyOTg3LCJpYXQiOjE3NDM3OTY5ODd9.Okv4g3LvBOmLajH4-5S2vUTheP5kLwhN5PrASOf87y8"
#bearer_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjb250ZXh0Ijp7ImJhc2VVcmwiOiJodHRwczovL2lpdGgtdGVhbS1xNHc2dnVyZi5hdGxhc3NpYW4ubmV0IiwidXNlciI6eyJhY2NvdW50SWQiOiI3MTIwMjA6ODYzYWQ0ZTctMDljNS00NjE1LThiZjgtZTQ3YzA3YmRkMjEzIiwidG9rZW5JZCI6IjUyZWUwMDVhLTM5OWMtNDQ2OC05YzJiLTVmMDVkZDEzNmU0YiJ9fSwiaXNzIjoiY29tLmthbm9haC50ZXN0LW1hbmFnZXIiLCJzdWIiOiJmNTY2ZjhjNi04OTc1LTNhMjQtODMzOC0xMzE3MjBmNjMxNjUiLCJleHAiOjE3NzUzMjMyODAsImlhdCI6MTc0Mzc4NzI4MH0.GO5UwzNYEfgUO5I9v2qrg5yaG5aislZaFlryM3wHpQc"
#bearer_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjb250ZXh0Ijp7ImJhc2VVcmwiOiJodHRwczovL2lpdGgtdGVhbS1xNHc2dnVyZi5hdGxhc3NpYW4ubmV0IiwidXNlciI6eyJhY2NvdW50SWQiOiI3MTIwMjA6ODYzYWQ0ZTctMDljNS00NjE1LThiZjgtZTQ3YzA3YmRkMjEzIiwidG9rZW5JZCI6IjJjNGQ1YWE3LTE5NjQtNDE3YS05OTRkLWFhNGUxM2E0NmEyNCJ9fSwiaXNzIjoiY29tLmthbm9haC50ZXN0LW1hbmFnZXIiLCJzdWIiOiJmNTY2ZjhjNi04OTc1LTNhMjQtODMzOC0xMzE3MjBmNjMxNjUiLCJleHAiOjE3NzUzMzIyMzcsImlhdCI6MTc0Mzc5NjIzN30.W_jYVzmzPfu9p2qt2o0HLVmTnmz5NEn1IgdGGbdOxuI"
make_authenticated_request(api_url, bearer_token)
