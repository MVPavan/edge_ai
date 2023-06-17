# import gi
# gi.require_version('Gst', '1.0')
# from gi.repository import Gst, GLib

# # Initialize GStreamer
# Gst.init(None)

# def get_final_node(root_node):
#     if isinstance(root_node.children, Node):
#         return get_final_node(root_node.children)
#     else:
#         return root_node


# class Node:
#     def __init__(self, val, children=None):
#         self.val = val
#         self.children = children if children is not None else []
#         self.element = None

# def create_element(element_name):
#     # Replace with specific initialization details
#     return Gst.ElementFactory.make(element_name, None)

# def create_pipeline_tree(plugins, root=None):
#     if isinstance(plugins, str):
#         return Node(plugins)

#     if isinstance(plugins[0], list):
#         root_child = [create_pipeline_tree(plugin) for plugin in plugins[0]]
#         child_nodes = create_pipeline_tree(plugins[1:])
#         for _node in root_child:
#             final_node = get_final_node(_node)
#             final_node.children = child_nodes
#         return root_child
#     else:
#         # If the first element is a string, it's a plugin
#         root = Node(plugins[0])
#         if len(plugins) > 1:
#             root.children = create_pipeline_tree(plugins[1:], root=root)
#     return root

# def add_and_link(pipeline, node, parent=None):
#     node.element = create_element(node.val)
#     pipeline.add(node.element)
#     if parent is not None:
#         parent.element.link(node.element)
#     for child in node.children:
#         add_and_link(pipeline, child, node)

# def main():
#     pipeline = Gst.Pipeline.new("test-pipeline")
#     plugins = ['videotestsrc', 'tee', [['queue1', 'autovideosink1'], ['queue2', 'autovideosink2']], 'autovideosink3',"fakesink"]
#     root = create_pipeline_tree(plugins)
#     add_and_link(pipeline, root)
#     pipeline.set_state(Gst.State.PLAYING)
#     try:
#         GLib.MainLoop().run()
#     except:
#         pass
#     pipeline.set_state(Gst.State.NULL)

# if __name__ == "__main__":
#     main()


# plugins = ['videotestsrc', 'tee', [['queue1', 'autovideosink1'], ['queue2', 'autovideosink2']], 'autovideosink3', 'fakesink']

# # Create a dictionary to store the linked plugins
# def create_linked_plugins_dict(plugins, linked_plugins = {}):    
#     # Iterate over the plugins list
#     for i, plugin in enumerate(plugins[::-1]):
#         # If the plugin is a string, add it to the linked plugins dictionary
#         if isinstance(plugin, str):
#             linked_plugins[plugin] = []
#         # If the plugin is a list, link its heads to the previous plugin and its tails to the subsequent plugin
#         elif isinstance(plugin, list):
#             # Link the heads to the previous plugin
#             if i > 0:
#                 for head in plugin[0]:
#                     linked_plugins[plugins[i-1]].append(head)
#             # Link the tails to the subsequent plugin
#             if i < len(plugins) - 1:
#                 for tail in plugin[1]:
#                     linked_plugins[tail] = [plugins[i+1]]

#     # Print the linked plugins dictionary
#     print(linked_plugins)

# create_linked_plugins_dict(plugins)


import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

def add_edge(graph, prev_node, next_node):
    if isinstance(next_node, list):
        for item in next_node:
            add_edge(graph, prev_node, item)
    else:
        graph.add_edge(prev_node, next_node)

def get_tuple_tail(tup, tail=[]):
    if not isinstance(tup[-1], tuple):
        return [tup[-1]]
    else:
        for elem in tup[::-1]:
            if isinstance(elem, tuple):
                tail.append(get_tuple_tail(elem[-1]))
        return tail



def handle_nested_list(graph, parent_list):
    for i in range(1, len(parent_list)):
        if isinstance(parent_list[i], tuple):
            [graph.add_edge(parent_list[i-1], parent_list[i][j][0]) for j in range(len(parent_list[i]))]
            [handle_nested_list(graph, parent_list[i][j]) for j in range(len(parent_list[i]))]

            # add_edge(graph, parent_list[i+1][-1], parent_list[i+2] if i+2 < len(parent_list) else None)
        elif isinstance(parent_list[i-1], tuple):
            for j in range(len(parent_list[i-1])):
                if isinstance(parent_list[i-1][j], tuple):
                    
                    graph.add_edge(parent_list[i-1][j][-1], parent_list[i])
                else:
                    graph.add_edge(parent_list[i-1][j][-1], parent_list[i])
            # [graph.add_edge(parent_list[i-1][j][-1], parent_list[i]) for j in range(len(parent_list[i-1]))]
        else:
            graph.add_edge(parent_list[i-1], parent_list[i])

# def handle_nested_list(graph, nested_list):
#     for i in range(len(nested_list) - 1):
#         if isinstance(nested_list[i], tuple):
#             last_node = handle_nested_list(graph, nested_list[i])
#             if i + 1 < len(nested_list):
#                 if isinstance(nested_list[i + 1], tuple):
#                     graph.add_edge(last_node, nested_list[i + 1][0])
#                 else:
#                     graph.add_edge(last_node, nested_list[i + 1])
#         else:
#             graph.add_node(nested_list[i])
#             if isinstance(nested_list[i + 1], tuple):
#                 graph.add_edge(nested_list[i], nested_list[i + 1][0])
#             else:
#                 graph.add_edge(nested_list[i], nested_list[i + 1])
#     return nested_list[-1]

def list_to_dag(input_list):
    G = nx.DiGraph()

    handle_nested_list(G, input_list)
    
    # nx.draw(G, with_labels=True, arrows=True)

    pos = nx.spring_layout(G, scale=5, k=0.5)
    d = dict(G.degree)
    # fig = plt.figure(figsize=(10, 10))
    # ax = fig.add_subplot(111)
    nx.draw(G, pos, node_color='lightblue', 
            with_labels=True, 
            nodelist=list(d.keys()), 
            node_size=[d[k]*100 for k in d],)
            # ax=ax)
    plt.savefig("dag.png")
def main():
    # input_list = ('a', 'b', (('c', 'd', (('e','e1'), ('f','f1'))), ('g', 'h')), 'i', 'j', 'k')
    input_list = ('a', 'b', (('c', 'd', (('e','e1'), ('f','f1')),"l"), ('g', 'h')), 'i', 'j', 'k')
    list_to_dag(input_list)


# def get_last_elements(tup):
#     # Check if the current tuple contains other tuples
#     nested = [t for t in tup if isinstance(t, tuple)]
    
#     # If it does, we iterate over them and call the function recursively
#     if nested:
#         # For each nested tuple, get its last elements
#         last_elements = [get_last_elements(t) for t in nested]
#         # Flatten the list of last elements
#         last_elements = [item for sublist in last_elements for item in sublist]
#     else:
#         # If there are no nested tuples, the last element is the last item of the tuple
#         last_elements = [tup[-1]]
#     return last_elements


if __name__ == "__main__":
    main()
