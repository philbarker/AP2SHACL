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


def make_property_shape_id(ps):
    """Return a URI id based on a property statement label & shape."""
    # TODO: allow user to set preferences for which labels to use.
    if ps.shapes == []:
        sh = "_"
    else:
        # using first shld be enough to dismbiguate
        # need to avoid unnecessary #s
        sh = quote(ps.shapes[0].replace("#", "").replace(" ", "").lower())
    if ps.labels == {}:
        id = URIRef("#" + sh + str(uuid4()).lower())
        return id
    else:
        languages = ps.labels.keys()
        if "en" in languages:
            label = ps.labels["en"]
        elif "en-US" in languages:
            label = ps.labels["en-US"]
        else:  # just pull the first one that's found
            label = list(ps.labels.values())[0]
        label = label[0].upper() + label[1:]  # lowerCamelCase
        id = URIRef("#" + sh + quote(label.replace(" ", "")))
        return id


def str2URIRef(namespaces, s):
    """Return a URIRef from a string that may be a URI or a curie."""
    if type(namespaces) is dict:
        pass
    else:
        msg = "Namespaces should be a dictionary."
        raise Exception(msg)
    if type(s) is str:
        pass
    else:
        msg = "value to convert should be a string."
        print(type(s))
        raise Exception(msg)
    if ":" in s:
        [pre, name] = s.split(":", 1)
        if pre == ("http" or "https"):
            return URIRef(s)
        elif pre in namespaces.keys():
            return URIRef(namespaces[pre] + name)
        else:
            # TODO logging/exception warning that prefix not known
            print("Warning: prefix ", pre, " not in namespace list.")
            return URIRef(s)
    else:
        # there's no prefix, just a string to convert to URI
        return URIRef(s)


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
        print("Warning: Node kind not matched.")
        return None


def list2RDFList(g, list, node_type, namespaces):
    """Convert a python list to an RDF list of items with specified node type"""
    # Currently only deals with lists that are all Literals or all IRIs
    # URIRef - already a rfdlib.URIRef ; anyURI text to convert to URIRef
    if not (node_type in ["Literal", "anyURI", "URIRef"]):
        msg = "Node type " + node_type + " unknown."
        raise Exception(msg)
    # useful to id list start node for testing
    if type(list[0]) is str or (type(list[0]) is URIRef):
        start_node_id = list[0].replace(":", "-")
        start_node_id = start_node_id.replace(" ", "-")
        start_node_id = start_node_id.replace("#", "")
        start_node_id = start_node_id.replace("_", "-")
    elif (type(list[0]) is int) or (type(list[0]) is float):
        start_node_id = list[0]
    else:
        start_node_id = None
    start_node = BNode(start_node_id)
    print(start_node)
    current_node = start_node
    for item in list:
        if node_type == "Literal":
            g.add((current_node, RDF.first, Literal(item)))
        elif node_type == "URIRef":
            g.add((current_node, RDF.first, item))
        elif node_type == "anyURI":
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
        self.ap = ap
        self.sg = Graph()  # shacl graph

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

    def convert_shapes(self):
        """Add the shapes from the application profile to the SHACL graph."""
        shapeInfo = self.ap.shapeInfo
        sh = "http://www.w3.org/ns/shacl#"
        for shape in shapeInfo.keys():
            shape_uri = URIRef(shape)
            self.sg.add((shape_uri, RDF.type, SH.NodeShape))
            if shapeInfo[shape]["label"]:
                label = Literal(shapeInfo[shape]["label"])
                self.sg.add((shape_uri, SH.name, label))
            if shapeInfo[shape]["comment"]:
                comment = Literal(shapeInfo[shape]["comment"])
                self.sg.add((shape_uri, SH.description, comment))
            if shapeInfo[shape]["target"] and shapeInfo[shape]["targetType"]:
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

    def convert_propertyStatements(self):
        """Add the property statements from the application profile to the SHACL graph as property shapes."""
        # TODO: untangle this : there must be repeats that can be factored out
        # TODO: consider if alterntves in sh.or could be special cases like type
        for ps in self.ap.propertyStatements:
            if len(ps.properties) > 1:
                ps_ids = []
                severity = self.convert_severity(ps.severity)
                for p in ps.properties:
                    prop = quote(p.replace("#", "").replace(":", "-"))
                    ps_id = make_property_shape_id(ps) + "-" + prop + "-opt"
                    ps_ids.append(ps_id)
                    ps_opt_uri = URIRef(ps_id)
                    path = str2URIRef(self.ap.namespaces, p)
                    self.sg.add((ps_opt_uri, RDF.type, SH.PropertyShape))
                    self.sg.add((ps_opt_uri, SH.path, path))
                    if ps.mandatory:
                        self.sg.add((ps_opt_uri, SH.minCount, Literal(1)))
                    if not ps.repeatable:
                        self.sg.add((ps_opt_uri, SH.maxCount, Literal(1)))
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
                ps_id = make_property_shape_id(ps)
                severity = self.convert_severity(ps.severity)
                ps_kind_uri = URIRef(ps_id + "_value")
                for sh in ps.shapes:
                    self.sg.add((URIRef(sh), SH.property, ps_kind_uri))
                self.sg.add((ps_kind_uri, RDF.type, SH.PropertyShape))
                for lang in ps.labels:
                    name = Literal(ps.labels[lang], lang=lang)
                    self.sg.add((ps_kind_uri, SH.name, name))
                for property in ps.properties:
                    path = str2URIRef(self.ap.namespaces, property)
                    self.sg.add((ps_kind_uri, SH.path, path))
                self.sg.add(((ps_kind_uri, SH.severity, severity)))
                if ps.valueNodeTypes != []:
                    nodeKind = convert_nodeKind(ps.valueNodeTypes)
                    self.sg.add((ps_kind_uri, SH.nodeKind, nodeKind))
                if ps.valueDataTypes != []:
                    for valueDataType in ps.valueDataTypes:
                        datatypeURI = str2URIRef(self.ap.namespaces, valueDataType)
                        self.sg.add((ps_kind_uri, SH.datatype, datatypeURI))
                if ps.valueConstraints != []:
                    sh_constrnt_type, constrnts = self.convert_valConstraints(ps)
                    for c in constrnts:
                        self.sg.add((ps_kind_uri, sh_constrnt_type, c))
                else:  # no value constraints to add
                    pass
                if ps.valueShapes != []:
                    for shape in ps.valueShapes:
                        self.sg.add((ps_kind_uri, SH.node, URIRef(shape)))
                if ps.mandatory or not ps.repeatable:
                    # Need separate property shape check that property is used correct number of times.
                    # Has to separated from other checks as failing ones of those might lead to wrong result on uniqueness.
                    ps_count_uri = URIRef(ps_id + "_count")
                    self.sg.add((ps_count_uri, RDF.type, SH.PropertyShape))
                    for property in ps.properties:
                        path = str2URIRef(self.ap.namespaces, property)
                        self.sg.add((ps_count_uri, SH.path, path))
                    if ps.mandatory:
                        self.sg.add((ps_count_uri, SH.minCount, Literal(1)))
                    if not ps.repeatable:
                        self.sg.add((ps_count_uri, SH.maxCount, Literal(1)))
                    for sh in ps.shapes:
                        self.sg.add((URIRef(sh), SH.property, ps_count_uri))
                    self.sg.add(((ps_count_uri, SH.severity, severity)))

    def convert_severity(self, severity):
        """Return SHACL value for severity based on string."""
        if severity == "":
            return SH.Info
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
        """Return SHACL value constraint type and list of constraints from property statement with single valueConstraint."""
        valueConstraints = ps.valueConstraints
        constraint_type = ps.valueConstraintType
        node_kind = convert_nodeKind(ps.valueNodeTypes)
        if constraint_type.lower == "picklist" or len(valueConstraints) > 1:
            if "Literal" in ps.valueNodeTypes:
                constraint_list = list2RDFList(
                    self.sg, valueConstraints, "Literal", self.ap.namespaces
                )
            elif "IRI" in ps.valueNodeTypes:
                constraint_list = list2RDFList(
                    self.sg, valueConstraints, "anyURI", self.ap.namespaces
                )
            else:
                raise Exception("Incompatible node kind and constraint.")
            return (SH_in, [constraint_list])  # return a list of one RDFList
        elif constraint_type == "":
            if "Literal" in ps.valueNodeTypes:
                constraint = Literal(valueConstraints[0])
            elif "IRI" in ps.valueNodeTypes:
                constraint = str2URIRef(self.ap.namespaces, valueConstraints[0])
            else:
                raise Exception("Incompatible node kind and constraint.")
            return (SH.hasValue, [constraint])
        elif constraint_type.lower() == "pattern":
            constraint = Literal(valueConstraints[0])
            return (SH.pattern, [constraint])
        elif constraint_type.lower() == "minlength":
            constraint = Literal(int((valueConstraints[0])))
            return (SH.minLength, [constraint])
        elif constraint_type.lower() == "maxlength":
            constraint = Literal(int((valueConstraints[0])))
            return (SH.maxLength, constraints)
        else:
            msg = "unknown type of value constraint: " + constraint_type
            raise Exception(msg)

    def dump_shacl(self):
        """Print the SHACL Graph in Turtle."""
        print("SHACL Dump:")
        print(self.sg.serialize(format="turtle"))
