import requests

# Primero loguear para obtener token
login_data = {
    "User_mail": "ascorread1",
    "password": "1234"
}

login_response = requests.post("http://localhost:8080/login", json=login_data)
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
    "Text": "Text publication whitout a image"
    #"Multimedia": {
        #"image_base64": base64_img,
        #"content_type": "image/png"
    #}
}

response = requests.post("http://localhost:8081/create-publication", json=publication_data, headers=headers)
print("Status:", response.status_code)
print("Respuesta:", response.json())
