import requests
import json

prompt = input("Chat:   ")

url1 = "https://ai.weiki.xyz/api/generate"
url = "http://192.168.1.18:11434/api/generate"
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}
data = {
    "model": "ecobike",
    "prompt": prompt
}
try:
# Sending the POST request with stream=True
    response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
    
    full_response = ""

    # Loop through the streamed lines of the response
    for line in response.iter_lines():
        if line:
            # Decode each line and load the JSON data
            data = json.loads(line.decode('utf-8'))
        
            # Accumulate the response text
            full_response += data.get('response', '')

            # If the response is done, break the loop
            if data.get('done'):
                break

    print(full_response)

except Exception as e:
    print(e)
