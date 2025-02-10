from dotenv import load_dotenv
import os

load_dotenv()

config = {  
    "MONGO_URI": os.getenv("MONGO_URI"),
    "SECRET_KEY": os.getenv("SECRET_KEY")
}

def get_config():
    return config






