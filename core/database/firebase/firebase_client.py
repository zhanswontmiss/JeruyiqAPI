import firebase_admin
from firebase_admin import credentials, firestore, auth

def init_firebase(app):
    """Initialize Firebase Admin SDK"""
    cred = credentials.Certificate(app.config['FIREBASE_CREDENTIALS'])
    firebase_admin.initialize_app(cred)
    
    # Initialize Firestore client
    db = firestore.client()
    app.extensions['firebase_db'] = db
    
    return db

def get_firebase_db():
    """Get the Firestore database instance"""
    from flask import current_app
    return current_app.extensions.get('firebase_db')
