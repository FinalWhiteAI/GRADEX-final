import firebase_admin
from firebase_admin import credentials, firestore
import os

# Get the absolute path to the directory containing this file (forms/)
dir_path = os.path.dirname(os.path.realpath(__file__))
# Join the directory path with the filename
cert_path = os.path.join(dir_path, 'serviceAcc.json')

cred = credentials.Certificate(cert_path)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()