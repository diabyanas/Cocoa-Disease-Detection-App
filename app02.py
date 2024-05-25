
# Python In-built packages
from pathlib import Path
import PIL

# External packages
import streamlit as st
import base64
import datetime
import uuid
import requests
import cv2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2 import service_account
import os
from dotenv import load_dotenv


# Modules locaux
import settings
from settings import *
from traitements import traitements
from functions import *


# Connexion à la base de données
db_connection_string = f"postgresql+psycopg2://postgres:Admin123@localhost:5432/cocoadb"
db_connection = DataBaseV2(
    db_name='cocoa-disease-detection',
    db_type='postgresql',
    db_user='postgres',
    db_password='Admin123',
    db_host='localhost',
    db_port=5432,
    db_url=None)


def send_prediction_request(image_data: bytes, confidence: float):
    try:
        # Vérification de la validité des données d'image
        if not isinstance(image_data, bytes):
            raise ValueError("Les données d'image doivent être de type bytes")
        
        url = "https://cocoa-disease-pred-api-d091f2c78d39.herokuapp.com/predict_image/"
        # url = "http://127.0.0.1:8001/predict_image/"
         
        files = {"image": image_data}
        data = {"confidence": confidence}
        
        response = requests.post(url, files=files, data=data)
        
        if response.status_code == 200:
            prediction_result = response.json()
            return prediction_result
        else:
            print("La requête a échoué avec le code de statut :", response.status_code)
            return None
    
    except requests.exceptions.RequestException as e:
        print("Une erreur s'est produite lors de l'envoi de la requête à l'API FastAPI :", e)
        raise ValueError("Erreur lors de l'envoi de la requête à l'API FastAPI")  # Lever explicitement une exception


# Configuration de la page Streamlit
st.set_page_config(
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)



dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

def send_email(subject, body):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    receiver_email = "diabyanas@gmail.com"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            text = msg.as_string()
            server.sendmail(sender_email, receiver_email, text)
            print("Email sent successfully!")  # Print success message
    except smtplib.SMTPAuthenticationError as e:
        print(f"Error sending email: {e}")  # Print error message






def myapp():
    # Configuration de la mise en page
    st.empty()

    # En-tête de la page principale
    st.markdown("<h2 style='text-align: center; color: white;'>Bienvenue sur l'Application de Détection des Maladies de la Cacao-Culture</h2>", unsafe_allow_html=True)

    # Barre latérale
    st.sidebar.header("Configuration du Modèle")

    confidence = float(st.sidebar.slider(
        "Niveau de Confiance", 25, 100, 50)) / 100

    #st.sidebar.header("Configuration de l'Image/Vidéo")
    source_radio = st.radio(
        "Source", settings.SOURCES_LIST)

    source_img = None

    # Surveillance

    start_time = None
    end_time = None
    response_time = None

    # Si une image est sélectionnée
    if source_radio == settings.IMAGE:
        source_img = st.sidebar.file_uploader(
            "Choisir une image...", type=("jpg", "jpeg", "png", 'bmp', 'webp'))

        col1, col2 = st.columns(2)

        with col1:
            try:
                if source_img is None:
                    pass
                else:
                    uploaded_image = PIL.Image.open(source_img)
                    st.image(uploaded_image, caption="Image téléchargée", use_column_width=True)
                            
            except Exception as ex:
                st.error("Une erreur s'est produite lors de l'ouverture de l'image.")
                st.error(ex)

        with col2:
            if source_img is None:
                pass
            else:
                if st.sidebar.button('Détecter les objets'):
                    image_bytes = source_img.getvalue()
                    start_time = datetime.datetime.now()
                    response = send_prediction_request(image_bytes, confidence)
                    end_time = datetime.datetime.now()
                    response_time = (end_time - start_time).total_seconds()
                    print("Réponse de l'API :", response)  

                    # Surveillance
                    st.sidebar.header("Monitoring")
                    st.sidebar.write(f"Confiance minimale : {round(response['confidence_min'], 2)*100} %")
                    st.sidebar.write(f"Réponse de l'API : {round(response_time,2)} secondes")

                    if response is not None and 'image_download_link' in response:
                        image_bbx_link = response['image_download_link']
                        # Remplacement de l'URL pour qu'elle pointe vers Heroku
                        image_bbx_link = image_bbx_link.replace("http://0.0.0.0:8001", "https://cocoa-disease-pred-api-d091f2c78d39.herokuapp.com")
                       
                        # Affichage de l'image après prédiction avec les boîtes englobantes
                        image = PIL.Image.open(requests.get(image_bbx_link, stream=True).raw)
                        st.image(image, caption="Image après prédiction", use_column_width=True)

                        # Surveillance
             
                        query = """
                            SELECT d.disease_name AS "Etat Santé", COUNT(d.disease_name) AS "Nombre"
                            FROM boxes b
                            INNER JOIN diseases d ON b.disease_id = d.disease_id
                            GROUP BY disease_name, d.disease_name
                            ORDER BY COUNT(d.disease_name) DESC;
                        """

                        query_result = db_connection.execute_query(query)

                        # Convertir le résultat en dataframe
                        if query_result is not None:
                            df_query_result = pd.DataFrame(query_result)

                            # Afficher les résultats dans la barre latérale avec un graphique à barres de taille réduite
                            st.sidebar.header(" ")
                            st.sidebar.bar_chart(df_query_result.set_index("Etat Santé"), width=300, height=200)  # Ajuster la largeur et la hauteur selon vos préférences

                        else:
                            st.sidebar.warning("Une erreur s'est produite lors de l'exécution de la requête.")




                    # Vérification des conditions pour envoyer l'e-mail
                    if confidence < 0.5 or response_time > 4:
                        subject = "Alerte : Niveau de confiance ou temps de réponse de l'api🚨🚨🚨"
                        body = """
                        🚨 Le niveau de confiance est inférieur à 50% ou le temps de réponse de l'API dépasse 4 secondes. 
                        Prière vérifier votre check-list pour éviter un arrêt de service ou une dégradation de service. 
                        Contacter le support Heroku au besoin pour plus d'actions proactives! 🚨
                        """
                        send_email(subject, body)


                    # Insertion dans la table pred_images
                    pred_img_id = None

                    if response is not None and 'pred_img_id' in response:
                        pred_img_id = response['pred_img_id']

                    db_connection.add_row("pred_images",
                                        pred_img_id=pred_img_id,
                                        user_id='ed2eaaeb-cb55-43c0-9992-fbd804540eb6',
                                        orig_img_path= '',
                                        det_img_path=image_bbx_link,
                                        #det_img_path=response['image_download_link'],
                                        date=datetime.datetime.now()
                                        )


                    # Insertion des données dans la table "boxes"
                    try:
                        bbx_and_conf_list = response['bbx_coordinates']
                        pred_img_id = response['pred_img_id']

                        if bbx_and_conf_list and pred_img_id:
                            for prediction in bbx_and_conf_list:
                                x_min, y_min, x_max, y_max, confidence = prediction

                                # Calcul du centre de la boîte
                                x_center = (x_min + x_max) / 2
                                y_center = (y_min + y_max) / 2

                                # Calcul de la largeur et de la longueur (en supposant que y_max représente le bas)
                                width = x_max - x_min
                                length = y_max - y_min

                                # Générer un seul UUID pour box_id en dehors de la boucle
                                box_id = uuid.uuid4()

                                # Itérer sur la liste des noms de maladies prédites
                                for disease_name in response['pred_classes']:
                                    # Récupérer l'identifiant de la maladie depuis la table "diseases"
                                    disease = db_connection.get_row("diseases", disease_name=disease_name)

                                    if disease:
                                        disease_id = disease[0]
                                    else:
                                        print(f"La maladie '{disease_name}' n'a pas été trouvée dans la base de données.")
                                        continue

                                    # Préparation des données pour l'insertion
                                    box_data = {
                                        "box_id": box_id,
                                        "disease_id": disease_id,
                                        "x_center": x_center,
                                        "y_center": y_center,
                                        "width": width,
                                        "length": length,
                                        "pred_img_id": pred_img_id,
                                        "confidence": confidence,
                                        "temps_reponse_api": response_time
                                    }

                                    # Insertion des données dans la table "boxes"
                                    db_connection.add_row("boxes", **box_data)

                        else:
                            print("Certains éléments nécessaires pour l'insertion dans la table 'boxes' sont manquants dans la réponse de l'API.")

                    except Exception as e:
                        print(f"Une erreur s'est produite lors de l'insertion des données dans la table 'boxes': {e}")

                        
    # Si 'pred_classes' est présent dans la réponse, afficher les traitements
    if 'pred_classes' in locals() or 'response' in locals():
        for pred_class in response['pred_classes']:
            if pred_class == "Healthy":
                st.write("🍫🌱 Un fruit sain a été détecté ! Prenez-en bien soin en suivant ces recommandations :")
                st.write("- Assurez-vous de maintenir les plantes en bonne santé.")
                st.write("- Effectuez une surveillance régulière pour détecter toute apparition de maladies ou de ravageurs.")
                st.write("- Appliquez des pratiques agricoles durables pour favoriser la croissance et la productivité.")
                st.write("- Utilisez des méthodes de lutte biologique pour contrôler les ravageurs sans nuire à l'environnement.")
            elif pred_class in traitements:
                st.subheader(f"Traitement pour la maladie : {pred_class}")
                st.write(traitements[pred_class]["treatments"])
                st.write("---")
            # else:
                # st.warning(f"Aucun traitement trouvé pour la maladie : {pred_class}")


    # if st.sidebar.button("Déconnexion"):
    #     st.write('<script type="text/javascript">location.reload(true);</script>', unsafe_allow_html=True)

# Exécutez l'application
if __name__ == "__main__":
    myapp()

