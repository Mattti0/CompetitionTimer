
import csv
from enum import Enum
import time

from competitor import Competitor


CLASS_IF_NOT_FOUND = "Check required"

class ExportLanguages(Enum):
    FI = 1,
    EN = 2

EXPORT_LANGUAGE = ExportLanguages.FI

class Competition():
    def __init__(self):
        self.__competition_name: str = ""
        self.start_time: float = 0
        self.end_time: float = 0
        self.competition_running: bool = False
        self.__participants: list[Competitor] = []
        self.__participants_finished: list[Competitor] = []
        self.__competition_classes: list[str] = []

    def __num_of_competitors(self):
        return len(self.__participants)

    def __get_temp_first_name(self):
        if EXPORT_LANGUAGE.name == "FI":
            return "Etunimi"

    def __get_temp_last_name(self):
        if EXPORT_LANGUAGE.name == "FI":
            return "Sukunimi"

    def get_duration(self):
        return time.time() - self.start_time
    
    def __find_competitor(self, bib_number: int) -> Competitor:
        for comp in self.__participants:
            if comp.get_bib_number() == bib_number:
                return comp
        return None
        
    def load_participants(self, path: str):
        try:
            with open(path, newline="", encoding="utf-8") as participants_csv:
                participants_reader = csv.reader(participants_csv, delimiter=";", quotechar="|")
                for entry_row in participants_reader:
                    competitor = Competitor(
                        etunimi=entry_row[1],
                        sukunimi=entry_row[2],
                        seura=entry_row[3],
                        kilpasarja=entry_row[4],
                        puhelinnumero="",
                        bibnumber=int(entry_row[0])
                    )

                    self.__participants.append(competitor)

                    if competitor.kilpasarja not in self.__competition_classes:
                        self.__competition_classes.append(competitor.kilpasarja)

                    print(competitor)

                print(f"Loaded {len(self.__participants)}")
                return len(self.__participants)
        except:
            return 0

    def start_competition(self):
        if self.competition_running:
            return False
        
        self.start_time = time.time()
        self.competition_running = True

        return True

    def finish_competition(self):
        if not self.competition_running:
            return False

        self.end_time = time.time()
        self.competition_running = False

        return True

    def competitor_finish(self, bib_number: int):
        if not self.competition_running:
            print("Couldn't finish competitor, competition not running")
            return None
        
        finish_time = self.get_duration()
        competitor = self.__find_competitor(bib_number)
        
        if not competitor:
            temp_competitor = Competitor(
                        self.__get_temp_first_name(), self.__get_temp_last_name(), "-", "-", CLASS_IF_NOT_FOUND, bib_number
            )
            self.__participants.append(temp_competitor)
            competitor = temp_competitor

        competitor.kirjaaAika(finish_time, 0)
        self.__participants_finished.append(competitor)

        return competitor

    def participant_not_finished(self, bib_number: int, cause: str):
        competitor = self.__find_competitor(bib_number)

        cause = cause.upper()
        print(cause)
        if competitor:
            if cause == "DNF":
                competitor.DNF()
            elif cause == "DSQ":
                competitor.DISQUALIFY()
            elif cause == "DNS":
                competitor.DNS()

            print(competitor)

            if competitor.isStatusOn():
                self.__participants_finished.append(competitor)

        return competitor
