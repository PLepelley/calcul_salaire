import pandas as pd
import math
import ics
from datetime import datetime
import os
from io import StringIO


class CalculSalaire():
    def __init__(self):
        self.nb_heure_jour = os.environ["NB_HEURE_JOUR"]
        self.nb_semaine_prsce_enfant_an = os.environ["NB_SEMAINE_PRSCE_ENFANT_AN"]
        self.nb_jour_mois = os.environ["NB_JOUR_MOIS"]
        self.frais_entretien_jour = os.environ["FRAIS_ENTRETIEN_JOUR"]
        self.salaire_horaire_net = os.environ["SALAIRE_HORAIRE_NET"]
        self.nb_heure_semaine = self.get_nb_heure_semaine()
        self.total_heure_mois = self.get_total_heure_mois()

    def get_nb_heure_semaine(self):
        nb_heure_semaine = self.nb_heure_jour*5
        return nb_heure_semaine      

    def get_total_heure_mois(self):
        nb_heure_semaine = self.get_nb_heure_semaine()
        total_heure_mois = (nb_heure_semaine * self.nb_semaine_prsce_enfant_an)/12
        return total_heure_mois

    def event_to_dict(self, event) -> dict:
        """function to get transform the event from ics file to list of dict

        Args:
            event (_type_): _description_

        Returns:
            dict: _description_
        """

        result = {
            "name": event.name,
            "begin": event.begin.date().strftime('%d-%m-%Y'),
            "duration_hours": event.duration.seconds / 3600,
            "duration_minutes" : event.duration.seconds / 60
        }
        
        return result
    
    def read_events(self, file):
        """_summary_

        Args:
            file (_type_): _description_
        """
        with open(file, "r") as f:
            icsFile = ics.Calendar(f.read())
            events = [self.event_to_dict(event) for event in icsFile.events]
        
        return events
    
    def read_event(self, uploaded_file):
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))

        # To read file as string:
        string_data = stringio.read()
        icsFile = ics.Calendar(string_data)
        events = [self.event_to_dict(event) for event in icsFile.events]
        return events

        
    def get_current_month(self) -> int:
        """function to get the first date of the current month

        Args:
            format (str): the format of the output wanted (values accepted:"AAAAMMJJ")

        Returns:
            str: _description_
        """
            
        current_month =  datetime.now().month


        # accept_format = ["AAAAMMJJ"]
        # if format not in accept_format:
        #     raise Exception('Format not supported')
        
        today = datetime.today() #get the current date
        first = today.replace(day=1) #get the first day of the month
        current_month = first.strftime("%Y-%m-%d") # set the format wanted
        return current_month

    def transform_event(self, events):
        """function to transform the events from ics file into dataframe with all columns to compute salary

        Args:
            events (_type_): _description_

        Returns:
            _type_: _description_
        """

        df_calendar = pd.DataFrame(events)
        df_calendar["begin"] = pd.to_datetime(df_calendar["begin"]).dt.normalize()
        df_calendar = df_calendar[df_calendar['name'] == "nounou"]
        df_current_month = df_calendar[df_calendar['begin'] >= self.get_current_month()]
        df_current_month['minutes_supp'] = df_current_month["duration_minutes"] - (8*60)
        df_current_month["frais_entretien"] = df_current_month.apply(lambda row: self.frais_entretien_jour if row['name'] == "nounou" else 0, axis=1)

        return df_current_month

    def get_heures_supp(self, df_current_month):
        """function to compute heure supp

        Args:
            df_current_month (_type_): _description_

        Returns:
            _type_: _description_
        """

        heures_supp = math.ceil(df_current_month['minutes_supp'].sum()/60)

        return heures_supp
    
    def get_frais_entretiens(self, df_current_month):
        """function to compute frais entretiens

        Args:
            df_current_month (_type_): _description_
        """
        frais_entretien = df_current_month["frais_entretien"].sum()

        return frais_entretien

    def calcul_salaire_net_mensuel(self) -> float:
        """function to compute the net salary per month

        Returns:
            float: the amount of the salary
        """

        salaire_net_mensuel = (self.salaire_horaire_net * self.nb_heure_semaine * self.nb_semaine_prsce_enfant_an) / 12

        return salaire_net_mensuel
    
    def calcul_salaire_heure_supp(self, heures_supp) -> float:
        """function to compute salary per month, including extra hours

        Returns:
            float: the amount of the salary to declaire
        """

        salaire_net_mensuel = self.calcul_salaire_net_mensuel()

        salaire_to_declare = salaire_net_mensuel + (heures_supp * self.salaire_horaire_net)

        return salaire_to_declare