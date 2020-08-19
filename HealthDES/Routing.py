""" HealthDES - A python library to support discrete event simulation in health and social care """

from __future__ import annotations

import networkx as nx

from dataclasses import dataclass

from typing import List, Dict, Optional, Tuple, Type, TYPE_CHECKING

# We are not import Activity and Decision, we are only using them for type checking.
# Note: import annotations from future for Python < 3.8
if TYPE_CHECKING:
    from .ActivityBase import ActivityBase
    from .DecisionBase import DecisionBase


@dataclass
class Activity:
    """Dataclass recording activity details within the routing database.
    """

    __slots__ = ["id", "graph_ref", "activity_class", "kwargs"]
    id: str
    graph_ref: Optional[Tuple[str, str, int]]
    activity_class: Optional[Type[ActivityBase]]
    kwargs: Optional[Dict]


@dataclass
class Decision:
    """Record recording activity details within the routing database.
    """

    __slots__ = ["id", "decision_class", "kwargs"]
    id: str
    decision_class: DecisionBase
    kwargs: Dict


class Routing:
    """Creates a routing graph which defines how people flow through care pathways.

    Care pathways are represented as routes in a directed graph. Each node represents a decision \
    point and each edge represents an activity. People are routed through the system making \
    decisions at each decision point as to which activity to do next. Activities specify how \
    environments, resources and people come together over a period of time.

    The routing graph consists of:
    + *Nodes:* Nodes are decision points within the routing network and determine which activity a \
    person will perform next. Nodes have a unique identifier and a routing function to determine \
    the next activity.
    + *Edges:* Edges are directed and represent activities within the system. An edge can start \
    and end on the same node (holding pattern). There is only one edge between adjacent nodes. \
    The edge has a unique activity function which is called to pull together environments, \
    resources and people.
    """

    def __init__(self):
        # G is a MultiDiGraph - a directed graph with multiple edges between the same nodes.
        self.G = nx.MultiDiGraph()

        # Dictionary of activities and reference to implementation classes
        self._activities: Dict[str, Activity] = {}
        self._decisions: Dict[str, Decision] = {}

    # Methods to interact with the activity dictionary
    def register_activity(self, activity: Activity) -> None:
        """Register an activity in the routing database. Only registered activities may \
        be used in the graph.
        Args:
            activity: Activity to register in the database, the id must be unique.

        Raises:
            ValueError: Raises an error if the id is not unique.
        """
        if self._activities.get(activity.id) is None:
            self._activities[activity.id] = activity
        else:
            raise ValueError(f"{activity.id} is not a unique activity ID.")

    def get_registered_activities(self) -> Optional[Dict[str, Activity]]:
        """Access the dictionary of registered activities.

        Returns:
            Returns the dictionary of registered activities.
        """
        return self._activities

    def get_activity(self, activity_id: str) -> Optional[Activity]:
        """Get an activity from the dictionary

        Args:
            activity_id: The id of the activity to access

        Returns:
            The activity recorded in the routing database.
        """
        return self._activities.get(activity_id)

    # Methods to interact with the activity dictionary
    def register_decision(self, decision: Decision) -> None:
        """Register a decision in the routing database. Only registered activities may \
        be used in the graph.

        Args:
            decision: Decision to register in the database, the id must be unique.

        Raises:
            ValueError: Raises an error if the id is not unique.
        """
        if self._decisions.get(decision.id) is None:
            self._decisions[decision.id] = decision
        else:
            raise ValueError(f"{decision.id} is not a unique decision ID.")

    def get_registered_decisions(self) -> Optional[Dict[str, Decision]]:
        """Access the dictionary of registered decisions.

        Returns:
            Returns the dictionary of registered decisions.
        """
        return self._decisions

    def get_decision(self, decision_id: str) -> Optional[Decision]:
        """Get a decisions from the dictionary

        Args:
            decision_id: The id of the decision to access

        Returns:
            The decision recorded in the routing database.
        """
        return self._decisions.get(decision_id)

    # TODO: This code will not work - we need both a valid node and Decision.
    def add_decision(self, decision_node: str) -> None:
        """Adds a decision to the routing graph.

        Args:
            decision_node: The name of the decision node to add to the graph.
        """
        if self.G.has_node(decision_node):
            print(f"Node {decision_node} already exists. Updating node.")
        self.G.add_node(decision_node, decision=self.get_decision(decision_node))

    # TODO: The return type needs defining as a dataclass if possible (collection, named tuple)
    def add_activity(
        self, activity_name: str, starting_node: str, ending_node: str
    ) -> Tuple[str, str, int]:
        """Adds an activity to the graph.

        Args:
            activity_name:The id of the activity to add to the graph (must exist in the Activity \
        database)
            starting_node: The starting node id.
            ending_node: The ending node id.

        Returns:
            Identifying co-ordinates for the activity (start node id, end node id, link identifier)
        """
        if not self.G.has_node(starting_node):
            print(f"Creating node {starting_node}")
        if not self.G.has_node(ending_node):
            print(f"Creating node {ending_node}")

        edge_key = self.G.add_edge(starting_node, ending_node, activity=activity_name)

        return (starting_node, ending_node, edge_key)

    # Methods to support routing person through the graph
    def get_decision_from_activity_ref(
        self, activity_ref: Tuple[str, str, int]
    ) -> Optional[Decision]:
        """Returns the decision that has to be taken once an activity completes

        Args:
            activity_ref (Tuple[str, str, int]): Edge co-ordinates for the activity within the graph

        Returns:
            Optional[Decision]: Returns a decision object, or None if there is no decision object \
        for that node
        """
        decision = self._decisions.get(activity_ref[1])

        return decision

    # TODO: We do not have a mechanism for working out the next list of activities (only returns
    # one at the moment)
    def get_activities_from_decision_id(
        self, decision_id: str
    ) -> Optional[List[Activity]]:
        """Given a decision node, gets the next activities in the graph.

        Args:
            decision_id: The node's decision_id

        Returns:
            Returns a list of next activities.
        """
        activity_list = []
        for u, v, k, activity_name in self.G.out_edges(  # type: ignore : Problem with NetworkX.
            nbunch=decision_id, keys=True, data="activity"
        ):
            activity = self._activities.get(activity_name)
            # Need to make sure that we are not sharing resources between instances.
            activity_list.append(
                Activity(
                    activity.id,
                    (u, v, k),
                    activity.activity_class,
                    activity.kwargs.copy(),
                )
            )

        return activity_list
