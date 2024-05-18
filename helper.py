from ultralytics import YOLO
import streamlit as st
import cv2
from pytube import YouTube
import settings
import os
import io
from settings import *

def load_model(model_path):
    # Chargement du modele
    model = YOLO(model_path)
    return model



def _display_detected_frames(conf, model, st_frame, image, is_display_tracking=None, tracker=None , ıou=0.5 ):
    """
        Affichage de l'objet détecté dans la vidéo
    """
    # Resize the image to a standard size
    image = cv2.resize(image, (720, int(720*(9/16))))

    # Display object tracking, if specified
    if is_display_tracking:
        res = model.track(image, conf=conf, persist=True, tracker=tracker ,iou=ıou )
    else:
    # Predict the objects in the image using the YOLOv8 model
        res = model.predict(image, conf=conf)


    # # Plot the detected objects on the video frame
    res_plotted = res[0].plot()
    st_frame.image(res_plotted,
                   caption='Detected Video',
                   channels="BGR",
                   use_column_width=True
                   )


def play_youtube_video(conf, model):
    """
    Affichage d'objet détecté dans les vidéos youtube
    """
    source_youtube = st.sidebar.text_input("YouTube Video url")

    #is_display_tracker, tracker ,ıou = display_tracker_options()

    if st.sidebar.button('Detect Objects'):
        try:
            yt = YouTube(source_youtube)
            stream = yt.streams.filter(file_extension="mp4", res=720).first()
            vid_cap = cv2.VideoCapture(stream.url)

            st_frame = st.empty()
            while (vid_cap.isOpened()):
                success, image = vid_cap.read()
                if success:
                    _display_detected_frames(conf,
                                             model,
                                             st_frame,
                                             image
                                             )

                else:
                    vid_cap.release()
                    break
        except Exception as e:
            st.sidebar.error("Error loading video: " + str(e))



def play_webcam(conf, model):
    """
    Affichage d'objet détecté depuis une webcam
    """
    source_webcam = settings.WEBCAM_PATH
    #is_display_tracker, tracker ,ıou = display_tracker_options()
    if st.sidebar.button('Detect Objects'):
        try:
            vid_cap = cv2.VideoCapture(source_webcam)
            st_frame = st.empty()
            while (vid_cap.isOpened()):
                success, image = vid_cap.read()
                if success:
                    _display_detected_frames(conf,
                                             model,
                                             st_frame,
                                             image,
                                             #is_display_tracker,
                                             #tracker,
                                             #ıou
                                             )
                else:
                    vid_cap.release()
                    break
        except Exception as e:
            st.sidebar.error("Error loading video: " + str(e))


def play_stored_video(conf, model):
    """
    Affichage d'objet depuis une simple vidéo uploadée
    """
    uploaded_files = st.file_uploader("Upload video files", key="video_uploader", type=["mp4", "avi", "mov"],
                                      accept_multiple_files=True)

    try:
        if uploaded_files is not None:
            for uploaded_file in uploaded_files:
                video_name = uploaded_file.name

            if video_name is not None:
                video_path = find_video_path_by_name(str(video_name), uploaded_files)
    except:
        st.warning("Please upload a video file available on your computer for inspection or tracking.")


    #is_display_tracker, tracker , ıou = display_tracker_options()

    if st.sidebar.button('Detect Video Objects'):
        try:
            vid_cap = cv2.VideoCapture(video_path)
            st_frame = st.empty()
            while (vid_cap.isOpened()):
                success, image = vid_cap.read()
                if success:
                    _display_detected_frames(conf,
                                             model,
                                             st_frame,
                                             image
                                             #is_display_tracker,
                                             #tracker ,
                                             #ıou
                                             )

                else:
                    vid_cap.release()
                    break
        except Exception as e:
            st.sidebar.error("Error loading video: " + str(e))


def show_model_not_loaded_warning(model):
    """
    Affichage de message quand il est impossible de charger le model
    """
    if model is None:
        st.warning("The model has not been loaded. Please upload a valid model weight file.")



def find_video_path_by_name(video_name , uploaded_files):
    """
    Retrouver le chemin des vidéos
    """

    if uploaded_files is not None:
        for uploaded_file in uploaded_files:
            if uploaded_file.name == video_name:
                # If the uploaded file matches the desired name, save it to a temporary location
                temp_location = save_uploaded_file(uploaded_file)
                if temp_location is not None:
                    return temp_location

    # If the desired video name was not found among the uploaded files
    return None


def save_uploaded_file(uploaded_file):
    try:
        temp_dir = io.BytesIO()
        temp_location = os.path.join(os.path.expanduser("detections/"), "Videos", uploaded_file.name)

        with open(temp_location, 'wb') as out:
            out.write(uploaded_file.read())

        return temp_location
    except Exception as e:
        st.error(f"Error saving uploaded file: {e}")
        return None





