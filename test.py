import requests

login_data = {
    "User_mail": "allan",
    "password": "1234"
}

login_response = requests.post("http://52.203.72.116:8080/login", json=login_data)
if login_response.status_code != 200:
    print("Login failed:", login_response.text)
    exit()

token = login_response.json().get("token")
print("Token:", token)

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

base64_img = "iVBORw0KGgoAAAANSUhEU"

publication_data = {
    "Text": "Publication"
    #"Multimedia": {
        #"image_base64": base64_img,
        #"content_type": "image/png"
    #}
}

response = requests.post("http://35.173.89.233:8080/create-publication", json=publication_data, headers=headers)
print("Status:", response.status_code)
print("Response:", response.json())

print("Status code:", response.status_code)
print("Raw response text:", response.text)

try:
    data = response.json()
    print("JSON response:", data)
except Exception as e:
    print("Error decoding JSON:", e)
