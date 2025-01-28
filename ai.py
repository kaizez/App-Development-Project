import requests
import json

def process_and_print_word_by_word(api_url, api_headers, model_name, user_prompt):
    data = {
        "model": model_name,
        "prompt": user_prompt
    }

    try:
        # Sending the POST request with stream=True
        response = requests.post(api_url, headers=api_headers, data=json.dumps(data), stream=True)

        # Loop through the streamed lines of the response
        for line in response.iter_lines():
            if line:
                # Decode each line and load the JSON data
                data = json.loads(line.decode('utf-8'))
                
                # Retrieve the response text
                chunk_response = data.get('response', '')

                # Split the response into words and print each word
                for word in chunk_response.split():
                    print(word, end=' ', flush=True)

                # If the response is done, break the loop
                if data.get('done'):
                    break

    except Exception as e:
        print(f"An error occurred: {e}")

# Input
prompt = input("Chat:   ")

# Configuration
url = "http://192.168.1.18:11434/api/generate"
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}
model = "ecobike-r1:latest"

# Execute
process_and_print_word_by_word(url, headers, model, prompt)