from AP import AP, PropertyStatement
from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib import SH, RDF, RDFS, XSD, SDO
from rdflib.collection import Collection
from uuid import uuid4
from urllib.parse import quote

# stoopid conflicts with python key words
SH_in = URIRef("http://www.w3.org/ns/shacl#in")
SH_or = URIRef("http://www.w3.org/ns/shacl#or")
SH_class = URIRef("http://www.w3.org/ns/shacl#class")

# default fallbacks for values that may be in AP metadata
default_language = "en"
default_base = "http://example.org/"


def make_property_shape_name(ps):
    """Return a URI id based on a property statement label & shape."""
    # TODO: allow user to set preferences for which labels to use.
    if ps.shapes == []:
        sh = "_"
    else:
        # using first shld be enough to dismbiguate
        # need to avoid unnecessary #s
        sh = quote(ps.shapes[0].replace("#", "").replace(" ", "").lower())
    if ps.labels == {}:
        name = sh + str(uuid4()).lower()
        return name
    else:
        languages = ps.labels.keys()
        if "en" in languages:
            label = ps.labels["en"]
        elif "en-US" in languages:
            label = ps.labels["en-US"]
        else:  # just pull the first one that's found
            label = list(ps.labels.values())[0]
        label = label[0].upper() + label[1:]  # lowerCamelCase
        name = sh + quote(label.replace(" ", ""))
        return name


def str2URIRef(namespaces, s):
    """Return a URIRef from a string that may be a URI or a curie."""
    if type(namespaces) is dict:
        pass
    else:
        msg = "Namespaces should be a dictionary."
        raise TypeError(msg)
    if type(s) is str:
        pass
    else:
        msg = "value to convert should be a string not " + type(s)
        raise TypeError(msg)
    if "base" in namespaces.keys():
        base = namespaces["base"]
    else:
        base = default_base
    if ":" in s:
        [pre, name] = s.split(":", 1)
        if pre == ("http" or "https"):
            return URIRef(s)
        elif pre in namespaces.keys():
            return URIRef(namespaces[pre] + name)
        else:
            # TODO logging/exception warning that prefix not known
            msg = "Prefix " + pre + " not in namespace list."
            raise ValueError(msg)
    else:
        # there's no prefix, convert to URI using base & URI safe str
        if (s[0] == "#") and (base[-1] == "#"):
            s = s[1:]
        return URIRef(base + quote(s))


def convert_nodeKind(node_TYPES):
    """Return a shacl nodeKind IRI based on list of permitted node types."""
    # first convert all permitted node type strings in list to lower case
    node_types = list((map(lambda x: x.lower(), node_TYPES)))
    if ("iri" in node_types) and ("bnode" in node_types) and ("literal" in node_types):
        return None
    if ("iri" in node_types) and ("bnode" in node_types):
        return SH.BlankNodeOrIRI
    elif ("iri" in node_types) and ("literal" in node_types):
        return SH.IRIOrLiteral
    elif ("bnode" in node_types) and ("literal" in node_types):
        return SH.BlankNodeOrLiteral
    elif "bnode" in node_types:
        return SH.BlankNode
    elif "iri" in node_types:
        return SH.IRI
    elif "literal" in node_types:
        return SH.Literal
    else:
        msg = "Node type " + node_type + " unknown."
        raise Exception(msg)
        return None


def list2RDFList(g, list, node_type, namespaces):
    """Convert a python list to an RDF list of items with specified node type"""
    # Currently only deals with lists that are all Literals or all IRIs
    # URIRef - already a rfdlib.URIRef ; anyURI text to convert to URIRef
    if not (node_type.lower() in ["literal", "anyuri", "uriref"]):
        msg = "Node type " + node_type + " unknown."
        raise ValueError(msg)
    # useful to id list start node for testing
    if type(list[0]) is str or (type(list[0]) is URIRef):
        if g.base and g.base in list[0]:
            start_node_id = quote(list[0].replace(g.base, ""))
        else:
            start_node_id = quote(list[0].replace(":", "_"))
    elif (type(list[0]) is int) or (type(list[0]) is float):
        start_node_id = list[0]
    else:
        start_node_id = None
    start_node = BNode(start_node_id)
    current_node = start_node
    for item in list:
        if node_type.lower() == "literal":
            g.add((current_node, RDF.first, Literal(item)))
        elif node_type.lower() == "uriref":
            g.add((current_node, RDF.first, item))
        elif node_type.lower() == "anyuri":
            item_uri = str2URIRef(namespaces, item)
            g.add((current_node, RDF.first, item_uri))
        if item == list[-1]:  # it's the last item
            g.add((current_node, RDF.rest, RDF.nil))
        else:
            next_node = BNode()
            g.add((current_node, RDF.rest, next_node))
            current_node = next_node
    return start_node


class AP2SHACLConverter:
    def __init__(self, ap):
        base = default_base
        self.ap = ap
        self.sg = Graph(base=base)  # shacl graph

    def convert_AP_SHACL(self):
        self.convert_namespaces()
        self.convert_shapes()
        self.convert_propertyStatements()

    def convert_namespaces(self):
        """Bind the namespaces in the application profle to the SHACL graph."""
        for prefix in self.ap.namespaces.keys():
            ns_uri = URIRef(self.ap.namespaces[prefix])
            ns = Namespace(ns_uri)
            self.sg.bind(prefix, ns)
            if "base" == prefix.lower():
                self.sg.base = ns_uri

    def convert_shapes(self):
        """Add the shapes from the application profile to the SHACL graph."""
        shapeInfo = self.ap.shapeInfo
        try:
            lang = self.ap.metadata["language"]
        except (KeyError, ValueError):
            lang = default_language
        sh = "http://www.w3.org/ns/shacl#"
        for shape in shapeInfo.keys():
            shape_uri = str2URIRef(self.ap.namespaces, shape)
            self.sg.add((shape_uri, RDF.type, SH.NodeShape))
            keys = shapeInfo[shape].keys()
            if ("label" in keys) and shapeInfo[shape]["label"]:
                label = Literal(shapeInfo[shape]["label"], lang=lang)
                self.sg.add((shape_uri, SH.name, label))
            if ("comment" in keys) and shapeInfo[shape]["comment"]:
                comment = Literal(shapeInfo[shape]["comment"], lang=lang)
                self.sg.add((shape_uri, SH.description, comment))
            if (
                ("target" in keys)
                and shapeInfo[shape]["target"]
                and ("targetType" in keys)
                and shapeInfo[shape]["targetType"]
            ):
                target = str2URIRef(self.ap.namespaces, shapeInfo[shape]["target"])
                if shapeInfo[shape]["targetType"].lower() == "class":
                    targetType = SH.targetClass
                elif shapeInfo[shape]["targetType"].lower() == "node":
                    targetType = SH.tagetNode
                elif shapeInfo[shape]["targetType"].lower() == "subjectsof":
                    targetType = SH.targetSubjectsOf
                elif shapeInfo[shape]["targetType"].lower() == "objectsof":
                    targetType = SH.targetObjectsOf
                self.sg.add((shape_uri, targetType, target))
            if ("closed" in keys) and shapeInfo[shape]["closed"] == True:
                self.sg.add(
                    (shape_uri, SH.closed, Literal("True", datatype=XSD.boolean))
                )
            elif ("closed" in keys) and shapeInfo[shape]["closed"] == False:
                self.sg.add(
                    (shape_uri, SH.closed, Literal("False", datatype=XSD.boolean))
                )
            if ("ignoreProps" in keys):
                print("ignore", shapeInfo[shape]["ignoreProps"])
                if shapeInfo[shape]["ignoreProps"]:
                    ignore = self.convert_uris(shapeInfo[shape]["ignoreProps"])
                    self.sg.add((shape_uri, SH.ignoredProperties, ignore))

    def convert_uris(self, uri_list):
        """Convert list of uriRefs to RDF List or single URI."""
        if type(uri_list) is not list:
            msg = "Properties to ignore must be a list."
            raise TypeError(msg)
        if len(uri_list) == 1:
            return str2URIRef(self.ap.namespaces, uri_list[0])
        else:
            return list2RDFList(self.sg, uri_list, "URIRef", self.ap.namespaces)



    def convert_propertyStatements(self):
        """Add the property statements from the application profile to the SHACL graph as property shapes."""
        # TODO: untangle this : there must be repeats that can be factored out
        # TODO: consider if alterntves in sh.or could be special cases like type
        for ps in self.ap.propertyStatements:
            if len(ps.properties) > 1:
                ps_ids = []
                severity = self.convert_severity(ps.severity)
                for p in ps.properties:
                    prop = quote(p.replace("#", "").replace(":", "_"))
                    ps_name = make_property_shape_name(ps) + "_" + prop + "_opt"
                    ps_id = str2URIRef(self.ap.namespaces, ps_name)
                    ps_ids.append(ps_id)
                    ps_opt_uri = str2URIRef(self.ap.namespaces, ps_name)
                    path = str2URIRef(self.ap.namespaces, p)
                    self.sg.add((ps_opt_uri, RDF.type, SH.PropertyShape))
                    self.sg.add((ps_opt_uri, SH.path, path))
                    if ps.mandatory:
                        self.sg.add((ps_opt_uri, SH.minCount, Literal(1)))
                    if not ps.repeatable:
                        self.sg.add((ps_opt_uri, SH.maxCount, Literal(1)))
                    if severity:
                        self.sg.add(((ps_opt_uri, SH.severity, severity)))
                or_list = list2RDFList(self.sg, ps_ids, "URIRef", self.ap.namespaces)
                self.sg.add((shape_uri, SH_or, or_list))
            elif ps.properties == ["rdf:type"]:
                # this is the way that TAP asserts objects must be of certain type, we can use sh:class instead
                for shape in ps.shapes:
                    shape_uri = str2URIRef(self.ap.namespaces, shape)
                    for vc in ps.valueConstraints:
                        type_uri = str2URIRef(self.ap.namespaces, vc)
                        self.sg.add((shape_uri, SH_class, type_uri))
                continue
            else:
                ps_name = make_property_shape_name(ps)
                severity = self.convert_severity(ps.severity)
                ps_uri = str2URIRef(self.ap.namespaces, ps_name)
                for sh in ps.shapes:
                    self.sg.add(
                        (str2URIRef(self.ap.namespaces, sh), SH.property, ps_uri)
                    )
                self.sg.add((ps_uri, RDF.type, SH.PropertyShape))
                for lang in ps.labels:
                    name = Literal(ps.labels[lang], lang=lang)
                    self.sg.add((ps_uri, SH.name, name))
                for property in ps.properties:
                    path = str2URIRef(self.ap.namespaces, property)
                    self.sg.add((ps_uri, SH.path, path))
                if severity:
                    self.sg.add(((ps_uri, SH.severity, severity)))
                if ps.valueNodeTypes != []:
                    nodeKind = convert_nodeKind(ps.valueNodeTypes)
                    if nodeKind is not None:
                        self.sg.add((ps_uri, SH.nodeKind, nodeKind))
                if ps.valueDataTypes != []:
                    for valueDataType in ps.valueDataTypes:
                        datatypeURI = str2URIRef(self.ap.namespaces, valueDataType)
                        self.sg.add((ps_uri, SH.datatype, datatypeURI))
                if ps.valueConstraints != []:
                    constr_dict = self.convert_valConstraints(ps)
                    for constr_type in constr_dict.keys():
                        for c in constr_dict[constr_type]:
                            self.sg.add((ps_uri, constr_type, c))
                else:  # no value constraints to add
                    pass
                if ps.valueShapes != []:
                    for shape in ps.valueShapes:
                        self.sg.add(
                            (ps_uri, SH.node, str2URIRef(self.ap.namespaces, shape))
                        )
                if ps.mandatory:
                    self.sg.add((ps_uri, SH.minCount, Literal(1)))
                if not ps.repeatable:
                    self.sg.add((ps_uri, SH.maxCount, Literal(1)))

    def convert_severity(self, severity):
        """Return SHACL value for severity based on string."""
        if severity == "":
            return ""
        elif severity.lower() == "info":
            return SH.Info
        elif severity.lower() == "warning":
            return SH.Warning
        elif severity.lower() == "violation":
            return SH.Violation
        else:
            msg = "severity not recognised: " + ps.severity
            raise Exception(msg)

    def convert_valConstraints(self, ps):
        """Return dict of SHACL value constraint types and lists of constraints from property statement with single valueConstraint."""
        valueConstraints = ps.valueConstraints
        constraint_type = ps.valueConstraintType
        node_kind = convert_nodeKind(ps.valueNodeTypes)
        if (constraint_type.lower() == "picklist") or (len(valueConstraints) > 1):
            if "literal" in ps.valueNodeTypes:
                constraint_list = list2RDFList(
                    self.sg, valueConstraints, "Literal", self.ap.namespaces
                )
            elif "iri" in ps.valueNodeTypes:
                constraint_list = list2RDFList(
                    self.sg, valueConstraints, "anyURI", self.ap.namespaces
                )
            else:
                raise Exception("Incompatible node kind and constraint.")
            return {SH_in: [constraint_list]}  # return a list of one RDFList
        elif constraint_type == "":
            if "Literal" in ps.valueNodeTypes:
                constraint = Literal(valueConstraints[0])
            elif "IRI" in ps.valueNodeTypes:
                constraint = str2URIRef(self.ap.namespaces, valueConstraints[0])
            else:
                raise Exception("Incompatible node kind and constraint.")
            return {SH.hasValue: [constraint]}
        elif constraint_type.lower() == "pattern":
            constraint = Literal(valueConstraints[0])
            return {SH.pattern: [constraint]}
        elif constraint_type.lower() == "minlength":
            constraint = Literal(int((valueConstraints[0])))
            return {SH.minLength: [constraint]}
        elif constraint_type.lower() == "maxlength":
            constraint = Literal(int((valueConstraints[0])))
            return {SH.maxLength: [constraint]}
        elif constraint_type.lower() == "lengthrange":
            [min, max] = (valueConstraints[0]).split("..")
            min_constraint = Literal(int(min))
            max_constraint = Literal(int(max))
            return {SH.maxLength: [max_constraint], SH.minLength: [min_constraint]}
        else:
            msg = "unknown type of value constraint: " + constraint_type
            raise Exception(msg)

    def dump_shacl(self, fname=None):
        """Print the SHACL Graph in Turtle."""
        if fname:
            try:
                f = open(fname, "w")
            except Exception as e:
                print("Could not open file %s for writing." % (fname))
                raise e
            f.write("# SHACL generated by python AP to shacl converter")
            f.write("\n")
            f.write(self.sg.serialize(format="turtle"))
            f.close()
        else:
            print("# SHACL generated by python AP to shacl converter")
            print(self.sg.serialize(format="turtle"))
