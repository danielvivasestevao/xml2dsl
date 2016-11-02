import xml.etree.ElementTree as Et


dsl_instance = []
open_ele_cnt = 0


def parse_xml(path_to_file):
    return make_dsl_instance(path_to_file)


def parse_node(node):
    if is_simple_node(node):
        parse_simple_node(node)
    else:
        parse_complex_node(node)


def parse_attributes(attrib_dict):
    for attrib, val in attrib_dict.items():
        make_simple_element(attrib, val)


def parse_complex_node(node):

    make_complex_obj_head(node.tag)

    for child in node:
        global open_ele_cnt
        open_ele_cnt += 1
        parse_node(child)
        open_ele_cnt -= 1

    if node.attrib:
        parse_attributes(node.attrib)

    make_complex_obj_tail()


def parse_simple_node(node):
    make_simple_element(node.tag, node.text)


########################
# STRING MANIPULATIONS #
########################

def make_dsl_instance(xml_file):
    tree = Et.parse(xml_file)
    root = tree.getroot()

    parse_node(root)

    return "\n".join(dsl_instance)


def make_simple_element(name, value):
    dsl_instance.append(
        "{} = {} ;".format(name, value)
    )


def make_complex_obj_head(name, flag):
    global open_ele_cnt

    if open_ele_cnt != 0:
        dsl_instance.append("{} = {{".format(name))
    else:
        dsl_instance.append("{")


def make_complex_obj_tail():
    global open_ele_cnt
    if open_ele_cnt != 0:
        dsl_instance.append("} ;")
    else:
        dsl_instance.append("}")


##########
# HELPER #
##########

def is_simple_node(node):
    if len(node) == 0 and not node.attrib:
        return True
    return False
