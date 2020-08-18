""" HealthDES - A python library to support discrete event simulation in health and social care """

import networkx as nx

from typing import List, Dict, Optional, Tuple, Type, TypeVar
from .ActivityBase import ActivityType, Activity
from .DecisionBase import DecisionType, Decision


class Routing():
    """Create a routing graph and than route people through the system

    The system is represented as a graph. Each node represents a decision point and each
    edge represents an activity. People are routed through the system making decisions at
    each decision point as to which activity to do next. Activities specify how environments,
    resources and people come together over a period of time.
    """

    def __init__(self):
        """Initialise graph

        The routing graph consists of:
        Nodes:      Nodes are decision points within the routing network and determine which
                    activity a person will perform next. Nodes have a unique identifier and a
                    routing function to determine the next activity.
        Edges:      Edges are directed and represent activities within the system. An edge can
                    start and end on the same node (holding pattern). There is only one edge
                    between adjacent nodes. The edge has a unique activity function which is
                    called to pull together environments, resources and people.
        """

        # G is a MultiDiGraph - a directed graph with multiple edges between the same nodes.
        self.G = nx.MultiDiGraph()

        # Dictionary of activities and reference to implementation classes
        self._activities: Dict[str, Activity] = {}
        self._decisions: Dict[str, Decision] = {}

    # Methods to interact with the activity dictionary
    def register_activity(self,
                          activity_id: str,
                          activity_class: Type[ActivityType],
                          **activity_kwargs: Dict) -> None:

        if self._activities.get(activity_id) is None:
            self._activities[activity_id] = Activity(activity_id, None, activity_class, activity_kwargs)
        else:
            raise ValueError(f'{activity_id} is not a unique activity ID.')

    def get_registered_activities(self) -> Optional[Dict[str, Activity]]:
        return self._activities

    def get_activity(self, activity_id: str) -> Optional[Activity]:
        return self._activities.get(activity_id)

    # Methods to interact with the activity dictionary
    def register_decision(self, decision_id: str,
                          decision_class: DecisionType,
                          **decision_kwargs: Dict) -> None:

        if self._decisions.get(decision_id) is None:
            self._decisions[decision_id] = Decision(decision_id, decision_class, decision_kwargs)
        else:
            raise ValueError(f'{decision_id} is not a unique decision ID.')

    def get_registered_decisions(self) -> Optional[Dict[str, Decision]]:
        return self._decisions

    def get_decision(self, decision_id: str) -> Optional[Decision]:
        return self._decisions.get(decision_id)

    # Methods to interact with the routing graph
    def add_decision(self, decision_node: str) -> None:
        """Create a decision point in the graph with decision function"""
        if self.G.has_node(decision_node):
            print(f'Node {decision_node} already exists. Updating node.')
        self.G.add_node(decision_node, decision=self.get_decision(decision_node))

    def add_activity(self, activity_name: str,
                     starting_node: str,
                     ending_node: str) -> Tuple[str, str, int]:
        """Create a directed between two nodes edge in the graph with a specific activity attached
        """
        if not self.G.has_node(starting_node):
            print(f'Creating node {starting_node}')
        if not self.G.has_node(ending_node):
            print(f'Creating node {ending_node}')

        edge_key = self.G.add_edge(starting_node, ending_node, activity=activity_name)

        return (starting_node, ending_node, edge_key)

    # Methods to support routing person through the graph
    def get_decision_from_activity_ref(self, activity_ref: Tuple[str, str, int]) -> Optional[Decision]:
        """Returns the decision that has to be taken once an activity completes

        Args:
            activity_ref (Tuple[str, str, int]): Edge co-ordinates for the activity within the graph

        Returns:
            Optional[Decision]: Returns a decision object, or None if there is no decision object for that node
        """

        decision = self._decisions.get(activity_ref[1])

        return decision

    def get_activities_from_decision_id(self, decision_id: str) -> Optional[List[Activity]]:
        activity_list = []
        for u, v, k, activity_name in self.G.out_edges(nbunch=decision_id, keys=True, data='activity'):  # type: ignore : Problem with NetworkX tuple count
            activity = self._activities.get(activity_name)
            # Need to make sure that we are not sharing resources between instances.
            activity_list.append(Activity(activity.id,
                                          (u, v, k),
                                          activity.activity_class,
                                          activity.kwargs.copy()))

        return activity_list


RoutingType = TypeVar('RoutingType', bound=Routing)
