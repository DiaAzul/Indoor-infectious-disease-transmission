""" Python library to model the spread of infectious diseases within a microenvironment """

from __future__ import annotations
from HealthDES.ActivityBase import kwargTypes
from HealthDES import ActivityBase
from Microenvironment import Microenvironment
from typing import Tuple, Dict, Type, cast


class VisitorActivity(ActivityBase):
    """Person's activity within the system, models interaction between people and environment """

    # The following pair of methods define the parametes passed to the activity.
    # The pack method is used to create the dictionary of parameters stored in
    # the activity dictionary. The method is static as it is called on the class
    # before an instance is created. The unpack parameter class is called when
    # the parameters are read from the activity dictionary and used to create an
    # actual instance of the activity prior to it being called (started).

    def unpack_parameters(self, **kwargs: kwargTypes) -> None:
        """Unpack the parameter list and store in local instance variables."""
        self.microenvironment = cast(Microenvironment, kwargs["microenvironment"])
        self.duration: int = cast(int, kwargs["duration"])

    @classmethod
    def pack_parameters(
        cls, microenvironment, duration
    ) -> Tuple[Type[ActivityBase], Dict[str, kwargTypes]]:
        """Pack parameters for the activity into a dictionary.

        Arguments:
            microenvironment {microenvironment obj} -- Microenvironment that the person will enter
            duration {number} -- Amount of time person spends in the environment

        Returns:
            Tuple(class, dictionary) -- This class and a dictionary of parameters required to
                                        instantiate an instance
        """
        # TODO: Rename as attributes and use existing mechanisms for setting and getting
        parameters: Dict[str, kwargTypes] = {
            "microenvironment": microenvironment,
            "duration": duration,
        }

        return (cls, parameters)

    def _seize_resources(self):
        self.request_entry = self.microenvironment.request_entry()
        yield self.request_entry

    def _do_activity(self):
        # Wait in the shop
        self.log_VisitorActivity(f"Visitor {self._person.id} entered.")
        self._sim_env.dc.counter_increment("Total visitors")

        person_request_to_leave = self._sim_env.env.event()

        if self._person.state["infection_status"] == "infected":
            self._sim_env.env.process(
                self.infected_visitor(
                    self.microenvironment.add_quanta_to_microenvironment,
                    person_request_to_leave,
                    self.duration,
                )
            )
            yield person_request_to_leave

        elif self._person.state["infection_status"] == "susceptible":

            self._sim_env.env.process(
                self.susceptible_visitor(
                    self.microenvironment.get_quanta_concentration,
                    person_request_to_leave,
                    self.duration,
                )
            )
            yield person_request_to_leave

        self.log_VisitorActivity(f"Visitor {self._person.id} left.")

    def infected_visitor(self, callback_add_quanta, request_to_leave, periods):
        """Callback from microenvironment for an infected person to generate quanta

        Args:
            callback_add_quanta: Callback to microenvironment to add quanta
            request_to_leave: Event notification to let microenvironment know we wish to leave to allow clean up before existing the microenvironment.
            periods: Number of periods person in the microenvironment

        Yields:
            Message: Periodic or end of period notification
        """
        end_trigger = self._sim_env.env.timeout(periods, value="end")

        while True:
            period_trigger = self._sim_env.env.timeout(1, value="periodic")

            # Add quanta to the environment
            quanta_emission_rate = self._person.attr["quanta_emission_rate"]
            self.microenvironment.add_quanta_to_microenvironment(
                quanta_emission_rate * self._sim_env.time_interval
            )

            fired_trigger = yield period_trigger | end_trigger
            if fired_trigger == {end_trigger: "end"}:
                break

        request_to_leave.succeed()

    def susceptible_visitor(
        self, callback_quanta_concentration, request_to_leave, periods
    ):
        """Callback from microenvironment for a susceptible person to calculate exposure

        Args:
            callback_quanta_concentration: callback to microenvironment to get quanta_concentration
            request_to_leave: Event notification to let microenvironment know we wish to leave to allow clean up before existing the microenvironment.
            periods: Number of period that person in the microenvironment

        Yields:
            Message: Periodic or end of period notification
        """
        end_trigger = self._sim_env.env.timeout(periods, value="end")

        while True:
            period_trigger = self._sim_env.env.timeout(1, value="periodic")

            # Assess exposure
            quanta_concentration = self.microenvironment.get_quanta_concentration()
            self._person.do(
                "expose_person_to_quanta", quanta_concentration=quanta_concentration
            )

            fired_trigger = yield period_trigger | end_trigger
            if fired_trigger == {end_trigger: "end"}:
                break

        request_to_leave.succeed()

    def log_VisitorActivity(self, activity):
        """Log visitor activity within the process visitor process

            Arguments:
            activity                  String describing the activity that has occurred.
        """

        self._sim_env.dc.log_reporting(
            "Visitor activity",
            {
                "queue": self.microenvironment.get_queue_length(),
                "visitors": self.microenvironment.get_active_users(),
                "activity": activity,
            },
        )
