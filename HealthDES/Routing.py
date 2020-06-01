""" Python library to model the spread of infectious diseases within a microenvironment """

import simpy
import networkx as nx

class Routing:
    """Create a routing graph and than route people throug the system

    The system is represented as a graph. Each node represents a decision point and each
    edge represents an activity. People are routed through the system making decisions at
    each decision point as to which activity to do next. Activities specifiy how environments,
    resources and people come together over a period of time.
    """

    def __init__(self):
        """Initialise graph

        The routing graph consists of:
        Nodes:      Nodes are decision points within the routing network and determine which
                    activity a person will perform next. Nodes have a unique identifier and a 
                    routing function to determine the next activity. 
        Edges:      Edges are directed and represent activities wthin the system. An edge can
                    start and end on the same node (holding pattern). There is only one edge
                    between adjacent nodes. The edge has a unique activity function which is
                    called to pull together environments, reources and people.
        """

        # G is a MultiDiGraph - a directed graph with multiple edges between the same nodes.
        self.G = nx.MultiDiGraph()

        # Dictionary of activities and reference to implementation classes
        self.activities = {}


    # Methods to interact with the activity dictionary

    def register_activity(self, activity_name, activity_class, arguments):
        """Register an activity with the activity registry

        Arguments:
            activity_name {string} -- Name of the activity to register
            activity_class {class ojb} -- Activity class, a child instance of this class
            arguments {dictionary} -- dictionary of arguments passed to the activity when called
        """
        self.activities[activity_name] = (activity_class, arguments)


    def get_activities(self):
        """Get the list of registered activities

        Returns:
            Dictionary -- Dictionary of registered activities.
        """        
        return self.activities


    def get_activity_details(self, activity_name):
        """Return a tuple containing the activity class and arguments

        Arguments:
            activity_name {string} -- Name of the activity

        Returns:
            (class obj, dictionary) -- Class for the activity, parameters to pass to activity when instance created
        """
        return self.activities[activity_name]


    # Methods to interact with the routing graph
    # TODO: Switch nodes and edges around - Node is the activity, edges are the transitions between activities (better for display)

    def add_decision(self, name):
        """Create a decision point in the graph with decision function"""

        node_id = self.G.add_node(name)

        return node_id

    def add_activity(self, name, starting_node, ending_node):
        """Create a directed between two nodes edge in the graph with a specific activity attached"""
        edge_id = self.G.add_edge(starting_node, ending_node, name)

        return edge_id


    def get_next_activity(self, node_id):
        """Determine the next activity, return both the activity and next node ID"""

        # Default no return values
        _, next_id, activity_id = (None, None, None)

        # TODO: This assumes we only have one possible edge from Node, the code will need to be developed
        # to include routing logic.
        if node_id:
            # For each of the available edges
            for items in self.G.out_edges(node_id, keys=True):
                _,  next_id, activity_id =  items
            activity_class, arguments = self.activities[activity_id]

        return next_id, activity_class, arguments





          