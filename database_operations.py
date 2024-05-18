# database_operations.py

def save_prediction_to_database(db, maladie_id, bbox, fruit_sain_id, sain, image):
    """
    Enregistre les prédictions dans la base de données PostgreSQL.

    Parameters:
        db (instance): Instance de la classe DataBaseV2.
        maladie_id (int): L'ID de la maladie détectée.
        bbox (str): Boîte englobante des objets détectés.
        fruit_sain_id (int): L'ID du fruit sain détecté.
        sain (bool): Indique si les objets sont sains ou non.
        image (bytes): L'image sur laquelle la détection a été effectuée (encodée en bytes).

    Returns:
        None
    """
    try:
        db.add_row('predictions', maladie_id=maladie_id, bbox=bbox, fruit_sain_id=fruit_sain_id, sain=sain, image=image)
        print("Prédictions enregistrées avec succès dans la base de données.")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement des prédictions dans la base de données : {str(e)}")
