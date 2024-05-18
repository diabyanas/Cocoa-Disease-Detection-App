# Packages intégrés à Python
from pathlib import Path
import PIL
import matplotlib.image
from functions import *

# Packages externes
import streamlit as st
import base64
import datetime
import pytz
import json 
import uuid
import hashlib  
from app02 import myapp


# Connexion à la base de données
db_connection_string = f"postgresql+psycopg2://postgres:Admin123@localhost:5432/cocoa-disease-detection"
db_connection = DataBaseV2(
    db_name='cocoa-disease-detection',
    db_type='postgresql',
    db_user='postgres',
    db_password='Admin123',
    db_host='localhost',
    db_port=5432,
    db_url=None)

# Fonction principale de l'application
session_state = st.session_state
def main_app():
    #session_state = st.session_state
    if 'loggedin' not in session_state:
        session_state.loggedin = False

    if session_state.loggedin:
        myapp()
    else:
        signin()

# Fonction de connexion des utilisateurs
def signin():
    nom_utilisateur = st.text_input("Entrez votre nom utilisateur :", key="nom_utilisateur")
    password = st.text_input("Entrez votre mot de passe :", type="password", key="password")
    email = st.text_input("Entrez votre adresse email :", key="adresse_email")
    
    # Vérifier l'authentification seulement si tous les champs sont remplis
    if nom_utilisateur and email and password:
        # Hacher le mot de passe avant de le comparer avec celui stocké dans la base de données
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        utilisateur = db_connection.get_row("users", nom_utilisateur=nom_utilisateur, password=hashed_password, email=email)

        if utilisateur:
            st.success("Connexion réussie !")
            session_state.loggedin = True
            st.rerun()  # Actualiser la page après une connexion réussie
        else:
            st.error("Email ou mot de passe incorrect")

    if st.button("Connexion"):
        signin()  
    

    st.markdown("---")
    st.subheader("Pas de compte ? Inscrivez-vous ici :")
    if session_state.loggedin == False:
        signup()


# Fonction de création de nouveaux comptes utilisateurs
def signup():
    nom_utilisateur = st.text_input("Entrez votre nom utilisateur :", key="nom_utilisateur_signup")
    password = st.text_input("Entrez votre mot de passe :", type="password", key="password_signup")
    email = st.text_input("Entrez votre adresse email :", key="adresse_email_signup")
    
    if st.button("S'inscrire"):
        if nom_utilisateur and email and password:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            utilisateur_existant = db_connection.get_row("users", email=email)

            if utilisateur_existant:
                st.error("L'adresse email est déjà utilisée")
            else:
                user_id = uuid.uuid4()
                db_connection.add_row("users", user_id=user_id ,nom_utilisateur=nom_utilisateur, password=hashed_password, email=email)
                st.success("Votre compte a été créé avec succès !")
                session_state.loggedin = True
    st.empty()
# Appel de la fonction principale de l'application
if __name__ == "__main__":
    main_app()

