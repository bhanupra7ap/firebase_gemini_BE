import re
import io
import firebase_admin
from firebase_admin import db, credentials
import google.generativeai as genai
import requests
import base64
from PIL import Image
from io import BytesIO


apiKey="AIzaSyA0JAcD2t3ctWfL5Y73KvYUYBFnzLVfe4I"

cred = credentials.Certificate("roboproject1-323f2-firebase-adminsdk-8ciaz-62c1d6970a.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://roboproject1-323f2-default-rtdb.asia-southeast1.firebasedatabase.app"})

def update_db(path, image):
    path_list = path.split('/')
    ref = db.reference("/")

    #ref.get()
    #dt  = db.reference("/").get()
    #image = dt["23-11-2024"]["G11"]["img"]
    
    img_data = base64.b64decode(image)
    img = Image.open(BytesIO(img_data))
    
    img_path = "plant_image.jpg"
    
    img.save(img_path)
    
    genai.configure(api_key=apiKey)
    image = genai.upload_file("plant_image.jpg")
    
    text_input = "Analyze the plant in the image for its information, growth and condition, such as disease, overwatering, or dryness  in minimum words in few lines and overall health condition as good or bad in one word. I want only the output that I asked and no opening and closing paragraph like Here is an analysis and similar sentences"
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([image, "\n\n", text_input])
    analysis_dict = response.text
    
    dt = db.reference(f"/{path_list[1]}/{path_list[2]}").update({"Details": analysis_dict})
    ref.get()


def listen_to_firebase_updates():
    ref = db.reference("/")
    def listener(event):
        if "/img" in event.path:
            #print(f"Event Type: {event.event_type}")
            image_path = event.path
            image = event.data
            
            update_db(image_path, image)
    ref.listen(listener)

listen_to_firebase_updates()
