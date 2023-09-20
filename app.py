import streamlit as st
from streamlit_calendar import calendar
from calcule_salaire import *
from io import StringIO
import os
from pathlib import Path


st.set_page_config(
    page_title="Gestion des salaires",
    page_icon=":baby:",
    layout="wide")

dest = '/tmp/files'

def makedir_if_not_exist(dest):
    if not os.path.exists(dest):
        os.makedirs(dest)

salaire = CalculSalaire()

st.header("Gestion des salaires des assistantes maternelles")
st.subheader("Calcul du salaire mensuel")
st.write(f"Mois : {salaire.get_current_month()}")




uploaded_file = st.file_uploader("Choisir un fichier (format accepté .ics)")
print(uploaded_file)
print(type(uploaded_file))

if uploaded_file is not None:

    if st.button("Calculer"):
        events = salaire.read_event(uploaded_file)

        df_current_month = salaire.transform_event(events)

        frais_entretiens = salaire.get_frais_entretiens(df_current_month)
        
        heures_supp = salaire.get_heures_supp(df_current_month)

        salaire_to_declare = salaire.calcul_salaire_heure_supp(heures_supp)
        data = [
            ("Frais d'entretiens", frais_entretiens), 
            ("Heures supplémentaires", heures_supp),
            ("Salaire à déclarer", salaire_to_declare),
            ("Nombre total heure par mois", salaire.total_heure_mois),
            ("Nombre de jours par mois",salaire.nb_jour_mois)
            ]
        df = pd.DataFrame(data, columns=['Clé', 'Valeur'])
        
        st.dataframe(df, hide_index= True, column_config=None)

    
        if st.button("Télécharger"):
            pass