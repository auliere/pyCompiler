import fileinput

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

# c - context module
def read_syntax_graph(c):
    nodes = {}
    depends = {}

    #EXPRESSIONS_STATES
    expr_nodes = []

    #START_LIST generates from depends[start_node]
    start_node = -1

    is_node = True
    for line in fileinput.input("syntax_graph.tgf"):
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