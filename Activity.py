""" Python library to model the spread of infectious diseases within a microenvironment """

from HealthDES import ActivityBase


class Visitor_activity(ActivityBase):
    """Person's activity within the system, models interaction between people and environment """

    # The following pair of methods define the parametes passed to the activity.
    # The pack method is used to create the dictionary of parameters stored in
    # the activity dictionary. The method is static as it is called on the class
    # before an instance is created. The unpack parameter class is called when
    # the parameters are read from the activity dictionary and used to create an
    # actual instance of the activity prior to it being called (started).

    def unpack_parameters(self, **kwargs):
        """Unpack the parameter list and store in local instance variables."""
        self.microenvironment = kwargs['microenvironment']
        self.duration = kwargs['duration']

    @classmethod
    def pack_parameters(cls, microenvironment, duration):
        """Pack parameters for the activity into a dictionary.

        Arguments:
            microenvironment {microenvironment obj} -- Microenvironment that the person will enter
            duration {number} -- Amount of time person spends in the environment

        Returns:
            Tuple(class, dictionary) -- This class and a dictionary of parameters required to
                                        instantiate an instance
        """

        parameters = {'microenvironment': microenvironment,
                      'duration': duration
                      }

        return cls, parameters

    def seize_resources(self):
        self.request_entry = self.microenvironment.request_entry()
        yield self.request_entry

    def execute(self):
        # Wait in the shop
        self.log_visitor_activity("Visitor {PID} entered.".format(PID=self.person.PID))
        self.dc.counter_increment('Total visitors')

        person_request_to_leave = self.env.event()

        if self.person.infection_status.is_state('infected'):
            self.env.process(self.infected_visitor(
                                            self.microenvironment.add_quanta_to_microenvironment,
                                            person_request_to_leave,
                                            self.duration))
            yield person_request_to_leave

        elif self.person.infection_status.is_state('susceptible'):

            self.env.process(self.susceptible_visitor(
                                            self.microenvironment.get_quanta_concentration,
                                            person_request_to_leave,
                                            self.duration))
            yield person_request_to_leave

        self.log_visitor_activity("Visitor {PID} left.".format(PID=self.person.PID))

    def infected_visitor(self, callback_add_quanta, request_to_leave, periods):
        """Callback from microenvironment for an infected person to generate quanta

            Arguments:
            callback_add_quanta             Callback to microenvironment to add quanta
            request_to_leave                Event notification to let microenvironment know we
                                            wish to leave to allow clean up before existing the
                                            microenvironment.
            periods                         Number of periods person in the microenvironment
         """

        end_trigger = self.env.timeout(periods, value='end')

        while True:
            period_trigger = self.env.timeout(1, value='periodic')

            # Add quanta to the environment
            quanta_emission_rate = self.person.get_attribute('quanta_emission_rate')
            self.microenvironment.add_quanta_to_microenvironment(
                                                    quanta_emission_rate * self.time_interval)

            fired_trigger = yield period_trigger | end_trigger
            if fired_trigger == {end_trigger: 'end'}:
                break

        request_to_leave.succeed()

    def susceptible_visitor(self, callback_quanta_concentration, request_to_leave, periods):
        """Callback from microenvironment for a susceptible person to calculate exposure

            Arguments:
            callback_quanta_concentration   callback to microenvironment to get quanta_concentration
            request_to_leave                Event notification to let microenvironment know we wish
                                            to leave to allow clean up before existing the
                                            microenvironment.
            periods                         Number of period that person in the microenvironment
        """
        end_trigger = self.env.timeout(periods, value='end')

        while True:
            period_trigger = self.env.timeout(1, value='periodic')

            # Assess exposure
            quanta_concentration = self.microenvironment.get_quanta_concentration()
            self.person.expose_person_to_quanta(quanta_concentration)

            fired_trigger = yield period_trigger | end_trigger
            if fired_trigger == {end_trigger: 'end'}:
                break

        request_to_leave.succeed()

    def log_visitor_activity(self, activity):
        """Log visitor activity within the process visitor process

            Arguments:
            activity                  String describing the activity that has occurred.
        """

        self.dc.log_reporting('Visitor activity',
                              {'queue': self.microenvironment.get_queue_length(),
                               'visitors': self.microenvironment.get_active_users(),
                               'activity': activity})
