""" HealthDES - A python library to support discrete event simulation in health and social care """

from __future__ import annotations
import inspect
import sys
import yaml
from simpy import Store

from typing import Callable, Union, Dict, Generator, Tuple, cast, Type

from .AttrActions import AttrActions

# We are not importing SimEnv, we are only using them for type checking.
# Note: import annotations from future for Python < 3.8
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .SimulationEnvironment import SimEnv


kwargTypes = Union[
    bool, bytes, str, int, float, complex, frozenset, Store, Callable, AttrActions
]


class ActivityBase:
    """Person's activity within the system, models interaction between people and environment """

    # The following dictionary defines the state diagram for the control loop
    _state_diagram = yaml.load(
        sys.intern(
            """
    init:
      initialise:
        next_state: initialised
        function: initialise
        success_message: initialised
    initialised:
      seize_resources:
        next_state: resources_seized
        function: seize_resources
        success_message: resources_seized
      start:
        next_state: running
        function: seize_resources_and_run
        success_message: completed
    resources_seized:
      start:
        next_state: completed
        function: do_activity
        success_message: completed
    completed:
      release_resources:
        next_state: stopped
        function: release_resources
        success_message: resources_released
      end:
        next_state: ended
        function: release_resources_and_end
        success_message: ended
    stopped:
      end:
        next_state: ended
        function: end
        success_message: ended
    """
        ),
        Loader=yaml.SafeLoader,
    )

    def __init__(self, sim_env: SimEnv, **kwargs: kwargTypes) -> None:

        self._sim_env = sim_env

        self._person: AttrActions = cast(AttrActions, kwargs.get("person"))
        self._message_to_activity: Store = cast(
            Store, kwargs.get("message_to_activity")
        )
        self._message_to_person: Store = cast(Store, kwargs.get("message_to_person"))

        self.unpack_parameters(**kwargs)

    def unpack_parameters(self, **kwargs: kwargTypes) -> None:
        raise NotImplementedError

    @classmethod
    def pack_parameters(
        cls: Type[ActivityBase], **kwargs: kwargTypes
    ) -> Tuple[Type[ActivityBase], Dict[str, kwargTypes]]:
        raise NotImplementedError

    def run(self) -> Generator[str, None, None]:
        """Run the event loop for the activity

        The event loop dispatches events in response to communication from the person class
        """
        function_dict = {
            "initialise": self._initialise,
            "seize_resources_and_execute": self._seize_resources_and_execute,
            "seize_resources": self._seize_resources,
            "do_activity": self._do_activity,
            "release_resources_and_end": self._release_resources_and_end,
            "release_resources": self._release_resources,
            "end": self._end,
        }

        state = "init"

        finished = False
        while not finished:
            # set an event flag to mark end of activity and call the activity class
            received_message = yield cast(str, self._message_to_activity.get())

            actions = ActivityBase._state_diagram.get(state, "NoState").get(
                received_message, "NoMessage"
            )
            if actions == "NoState":
                raise ValueError("Activity state error")
            if actions == "NoMessage":
                raise ValueError("Activity received message error")

            next_state = actions["next_state"]
            action = actions["function"]
            success_message = actions["success_message"]

            if not function_dict.get(action, None):
                raise ValueError(f"Activity function {action} missing")

            # Check whether subclassed method is a generator, which requires
            # different calling pattern
            if inspect.isgeneratorfunction(function_dict.get(action)):
                for result in function_dict.get(action)():
                    pass
            else:
                function_dict.get(action)()

            state = next_state

            self._message_to_person.put(success_message)

            finished = True if state == "ended" else finished

    def _nop(self) -> None:
        pass

    def _initialise(self) -> None:
        pass

    def _seize_resources_and_execute(self) -> None:
        self._seize_resources()
        self._do_activity()

    def _seize_resources(self) -> None:
        pass

    def _do_activity(self) -> None:
        pass

    def _release_resources_and_end(self) -> None:
        self._release_resources()
        self._end()

    def _release_resources(self) -> None:
        pass

    def _end(self) -> None:
        pass
