""" Python library to model the spread of infectious diseases within a microenvironment """

from HealthDES.Check import CheckList


class DiseaseProgression:
    """ Disease status of person within the model """

    disease_states = ['susceptible', 'exposed', 'infected', 'recovered']

    def __init__(self, infection_status_label: str = None):
        """ All people have an initial status of susceptible """

        self.status = DiseaseProgression.valid_state('susceptible') if infection_status_label is None else DiseaseProgression.valid_state(infection_status_label)

    @staticmethod
    def valid_state(infection_status_label: str) -> str:
        """ Checks text and returns text if it is a valid disease state """

        CheckList.fail_if_not_in_list(infection_status_label, DiseaseProgression.disease_states)
        return infection_status_label

    def set_state(self, infection_status_label: str) -> None:
        """ Sets the disease state """

        CheckList.fail_if_not_in_list(infection_status_label, DiseaseProgression.disease_states)
        self.status = infection_status_label

    def is_state(self, infection_status_label: str) -> bool:
        """ Tests disease state and return True if matches """

        CheckList.fail_if_not_in_list(infection_status_label, DiseaseProgression.disease_states)
        return self.status == infection_status_label
