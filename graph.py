import fileinput
import os

def get_type(n, c):
    TGF_RESERVED_WORDS = {
        'IDENT' : c.T_VAR,
        'STRING' : c.T_STRING,
    }

    if n in TGF_RESERVED_WORDS:
        return TGF_RESERVED_WORDS[n]

    elif n.strip('"') in c.RESERVED_WORDS:
        return c.RESERVED_WORDS[n.strip('"')]

    elif n.strip('"') in c.SYMB_DICT:
        return c.SYMB_DICT[n.strip('"')]

def general_graph(c):
    nodes = {}
    depends = {}

    #EXPRESSIONS_STATES
    expr_nodes = []

    #START_LIST generates from depends[start_node]
    start_node = -1

    is_node = True
    for line in fileinput.input("tgf/syntax_graph.tgf"):
        if line.strip() == "#":
            is_node = False
            continue

        parts = line.split(" ")
        num = int(parts[0])
        if is_node:
            name = ' '.join(parts[1:]).strip()
            p = name.split("-")
            if len(p)>1:
                function = p[-1].strip()
                name = '-'.join(p[:-1]).strip()
            else:
                function = None

            token_type = get_type(name, c)
            if name == "START":
                start_node = num
            if name == "EXPR":
                expr_nodes.append(num)
            nodes[num] = (name, [token_type], function)
            depends[num] = []
        else:
            num_to = int(parts[1].strip())
            depends[num].append(num_to)
     
    links = {}
    for node_id, node in nodes.iteritems():
        links[node_id] = (depends[node_id], node[1], node[2], start_node == node_id)

    #print links
    # Filling utils.const
    c.links = links
    c.EXPRESSIONS_STATES = expr_nodes
    c.START_NODE = start_node
    c.START_LIST = depends[start_node]

def expressions_graph(c):
    dict_nodes = {}
    path = "tgf/expressions.d/"
    for f_name in sorted([ os.path.join(path,f) for f in os.listdir(path) if os.isfile(os.path.join(path,f)) ]):
        nodes = {}
        depends = {}

        #EXPRESSIONS_STATES
        expr_nodes = []

        #START_LIST generates from depends[start_node]
        start_node = -1
        is_dict_tree = False

        is_node = True

        for line in fileinput.input(f_name):
            if line.strip() == "#":
                is_node = False
                if not is_dict_tree:
                    #main file. add nodes for all additional
                    new_id = max(nodes) + 1
                    for key,dict_node in dict_nodes.iteritems():
                        new_dict = {}
                        for node in reversed(dict_node[0]):
                             new_dict[new_id] = dict_node[0][node]
                             #TODO:
                        nodes.update(new_dict)
                continue

            parts = line.split(" ")
            num = int(parts[0])
            if is_node:
                name = ' '.join(parts[1:]).strip()
                p = name.split("-")
                if len(p)>1:
                    function = p[-1].strip()
                    name = '-'.join(p[:-1]).strip()
                else:
                    function = None

                token_type = get_type(name, c)
                if name == "START":
                    start_node = num
                if name == "EXPR":
                    expr_nodes.append(num)
                if name[0] == "$" and name[-1] == ':':
                    is_dict_tree = True
                    start_node = num
                    dict_tree_name = name[1:-1]

                nodes[num] = (name, [token_type], function)
                depends[num] = []
            else:
                num_to = int(parts[1].strip())
                to_name = nodes[num_to][0]
                if to_name[0] == "$" and to_name[-1] != ":":
                    pass
                depends[num].append(num_to)

        if is_dict_tree:
            dict_nodes[dict_tree_name] = (nodes, depends)
     
    links = {}
    for node_id, node in nodes.iteritems():
        links[node_id] = (depends[node_id], node[1], node[2], start_node == node_id)

    #print links
    # Filling utils.const
    c.E_LINKS = links
    c.E_EXPRESSIONS_STATES = expr_nodes
    c.E_START_NODE = start_node
    c.E_START_LIST = depends[start_node]

# c - context module
def read_syntax_graph(c):
    general_graph(c)
    expressions_graph()