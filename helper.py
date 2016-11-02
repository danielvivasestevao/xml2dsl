from xsd2ebnf import xsd2ebnf, xsd_elems


def is_simple_node(node):
    if len(node) != 0:
        return False

    if "type" in node.attrib:
        return True
    else:
        if "ref" in node.attrib:
            return True

    return False


def is_attribute(node):
    if xsd_elems[node.tag] == "attribute":
        return True
    return False


def is_builtin_datatype(type_):
    if type_ in xsd2ebnf:
        return True
    return False


def get_multiplicity(node):
    attrs = node.attrib

    min_occurs = None
    max_occurs = None

    if "minOccurs" in attrs:
        min_occurs = attrs["minOccurs"]
    if "maxOccurs" in attrs:
        max_occurs = attrs["maxOccurs"]

    if not min_occurs and not max_occurs:
        return None

    if min_occurs and max_occurs:
        if (min_occurs == "1") and (max_occurs == "unbounded"):
            return "+"
        elif (min_occurs == "0") and (max_occurs == "1"):
            return "?"
        elif (min_occurs == "0") and (max_occurs == "unbounded"):
            return "*"
        else:
            return None

    if max_occurs:
        if max_occurs == "unbounded":
            return "+"
        elif max_occurs == "1":
            return "?"
        else:
            return None

    if min_occurs:
        if min_occurs == "0":
            return "*"
        elif min_occurs == "1":
            return "+"
        else:
            return None


def get_use(node):
    attrs = node.attrib

    try:
        if attrs["use"] == "required":
            return ""
    except KeyError:
        return "?"
