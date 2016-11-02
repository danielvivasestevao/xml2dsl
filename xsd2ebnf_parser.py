from os.path import basename, splitext
import xml.etree.ElementTree as Et
import helper
from xsd2ebnf import xsd2ebnf, antlr_grammar_start, ANTLR_GRAMMAR_END,\
    xsd_elems


antlr4_grammar = []
type_rules = set()
open_ele_cnt = 0


def parse_xsd(path_to_file):
    """
    # Example use that saves the generated grammar in the same directory:

    xsd_file = "Company.xsd"
    antlr_string = parse_xsd(xsd_file)
    with open("Company.g4", "w") as f:
        f.write(antlr_string)
    """
    return make_grammar(path_to_file)


def parse_node(node):
    if ((xsd_elems[node.tag] == "complexType" and "name" not in node.attrib)
        or xsd_elems[node.tag] == "sequence"):
        for child in node:
            global open_ele_cnt
            open_ele_cnt += 1
            parse_node(child)
            open_ele_cnt -= 1

    else:

        if helper.is_simple_node(node):
            parse_simple_node(node)
        else:
            parse_complex_node(node)


def parse_simple_node(node):
    attrs = node.attrib
    try:
        name = attrs["name"]
    except KeyError:
        name = attrs["ref"]
    type_ = None

    # elements

    # element with type
    try:
        type_ = make_type_rule(attrs["type"])
    except KeyError:

        # element with ref
        try:
            type_ = attrs["ref"].lower()
        except Exception:
            raise Exception("Simple node with neither 'type' nor 'ref'")

    multiplicity = helper.get_multiplicity(node)

    # attributes

    usage = None
    if helper.is_attribute(node):
        # attribute with fixed value
        try:
            type_ = attrs["fixed"]
        except KeyError:
            pass

        # attribute with optional usage
        # (disregard "default" attribute)
        usage = helper.get_use(node)

    make_simple_element(name, type_, usage, multiplicity)


def parse_complex_node(node):
    attrs = node.attrib
    name = attrs["name"]
    multiplicity = helper.get_multiplicity(node)

    make_complex_element_head(name, multiplicity)

    for child in node:
        global open_ele_cnt
        open_ele_cnt += 1
        parse_node(child)
        open_ele_cnt -= 1

    make_complex_element_foot(multiplicity)


##################
# STRING METHODS #
##################

def make_complex_element_head(name, multiplicity=None):
    global open_ele_cnt

    if open_ele_cnt != 0:
        if multiplicity:
            antlr4_grammar.append(
                "( '{}' '=' '{{'".format(name.title())
            )
        else:
            antlr4_grammar.append(
                "'{}' '=' '{{'".format(name.title())
            )
    else:
        if multiplicity:
            antlr4_grammar.append(
                "( {} : '{{'".format(name.lower())
            )
        else:
            antlr4_grammar.append(
                "{} : '{{'".format(name.lower())
            )


def make_complex_element_foot(multiplicity=None):
    global open_ele_cnt

    if open_ele_cnt != 0:
        if multiplicity:
            antlr4_grammar.append("'}}'){} ';'".format(multiplicity))
        else:
            antlr4_grammar.append("'}' ';'")
    else:
        if multiplicity:
            antlr4_grammar.append("'}}'){} ;".format(multiplicity))
        else:
            antlr4_grammar.append("'}' ;")


def make_simple_element(name, type_, indicator=None, multiplicity=None):
    # one line elements
    # type_ can be a fixed value

    if open_ele_cnt == 0:
        name = name.lower()
        operator = ":"
        semicolon = ";"
    else:
        name = "'{}'".format(name.title())
        operator = "'='"
        semicolon = "';'"

    if indicator and multiplicity:
        line = "(({} {} {}){} {}){}"\
            .format(name, operator, type_, indicator, semicolon, multiplicity)
    elif indicator:
        line = "({} {} {}){} {}"\
            .format(name, operator, type_, indicator, semicolon)
    elif multiplicity:
        line = "({} {} {} {}){}"\
            .format(name, operator, type_, semicolon, multiplicity)
    else:
        line = "{} {} {} {}".format(name, operator, type_, semicolon)

    antlr4_grammar.append(line)


def make_grammar(xsd_file):
    tree = Et.parse(xsd_file)

    antlr4_grammar.append(
        # grammar name = file name
        antlr_grammar_start(splitext(basename(xsd_file))[0].title())
    )

    antlr4_grammar.append("// PARSER RULES")

    for node in tree.getroot():  # tree.getroot() is <xs:schema>
        parse_node(node)

    antlr4_grammar.append("// TYPE RULES")
    antlr4_grammar.extend(type_rules)

    antlr4_grammar.append(ANTLR_GRAMMAR_END)

    return "\n".join(antlr4_grammar)


def make_type_rule(type_):
    try:
        parser_rule_body, type_rule, dependencies = xsd2ebnf[type_]
    except KeyError:
        return type_.lower()  # if type is a custom type, defined in the xsd

    type_rules.add(type_rule)

    while dependencies:
        x, type_rule, dep2 = xsd2ebnf[dependencies.pop()]
        dependencies = dependencies.union(dep2)
        type_rules.add(type_rule)

    return parser_rule_body
