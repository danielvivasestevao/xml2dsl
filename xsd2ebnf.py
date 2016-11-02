def antlr_grammar_start(grammar_name):
    return " ".join(["grammar", grammar_name, ";", "\n"])

ANTLR_GRAMMAR_END = "WS : [ \\t\\r\\n]+ -> skip ; // skip spaces, tabs, newlines"

# Lexer rules for XSD built-in datatypes
xsd2ebnf = {
    # lexical representation of primitive datatypes
    # semantic analysis is delegated to parsing time in the Java code
    "xs:string": ("STRING+",
                  "STRING : ([a-zA-Z])+ ;",
                  set()),
    "xs:boolean": ("BOOL_TYPE",
                   "BOOL_TYPE : 'true' | 'false' | '0' | '1' ;",
                   set()),
    "xs:decimal": ("decimal_type",
                   "decimal_type : ('+' | '-')? (INT)? ('.' INT)? ;",
                   {"xs:int"}),
    "xs:float": ("float_type",
                 "float_type :  (decimal_type ('E' ('+' | '-')? INT)?) | '-'? 'INF' | 'NaN' ;",
                 {"xs:decimal"}),
    "xs:double": ("double_type",
                  "double_type : float_type ;",
                  {"xs:float"}),
    # "xs:duration": "",
    # "xs:dateTime": "",
    # "xs:time": "",
    # "xs:date": "",
    # "xs:gYearMonth": "",
    # "xs:gYear": "",
    # "xs:gMonthDay": "",
    # "xs:gDay": "",
    # "xs:gMonth": "",
    # "xs:hexBinary": "",
    # "xs:base64Binary": "",
    # "xs:anyURI": "",
    # "xs:QName": "",
    # "xs:NOTATION": "",

    "xs:int": ("INT", "INT : [0-9]+ ;", set())
}


# XSD element types
prefix = "{http://www.w3.org/2001/XMLSchema}"
element_types = ["element", "attribute", "simpleType", "complexType",
                 "sequence", "simpleContent", "complexContent", "restriction",
                 "extension"]
xsd_elems = {prefix + e: e for e in element_types}
