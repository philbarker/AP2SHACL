import pytest
from AP2SHACL import (
    AP2SHACLConverter,
    make_property_shape_name,
    list2RDFList,
    AP,
    PropertyStatement,
    ShapeInfo,
    read_shapeInfoDict,
    str2URIRef,
    convert_nodeKind,
)
from rdflib import Graph, URIRef, Literal, BNode, Namespace, RDF, RDFS, SH

schema = Namespace("https://schema.org/")
SDO = Namespace("https://schema.org/")  # "httpS"
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
BASE = Namespace("http://example.org/shapes#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
# avoid stoopid conflicts python keywords
SH_in = URIRef("http://www.w3.org/ns/shacl#in")
SH_or = URIRef("http://www.w3.org/ns/shacl#or")
SH_class = URIRef("http://www.w3.org/ns/shacl#class")
expected_triples = []  # used to test for triples expected in graph
expected_ttl = []  # used for to test for prefixes and lists expected in graph
# because (a) not triples, (b) blank nodes not reproducible


@pytest.fixture(scope="module")
def name_ps():
    ps = PropertyStatement()
    ps.add_shape("#Person")
    ps.add_property("schema:name")
    ps.add_label("en", "Name")
    ps.add_label("es", "Nombre")
    ps.add_valueNodeType("literal")
    ps.add_valueDataType("xsd:string")
    ps.add_valueDataType("rdf:langString")
    ps.add_valueConstraintType("minLength")
    ps.add_valueConstraint("2")
    ps.add_mandatory(True)
    ps.add_repeatable(True)
    ps.add_severity("Violation")
    expected_triples.extend(
        [
            (BASE.Person, SH.property, BASE.personName),
            (BASE.personName, RDF.type, SH.PropertyShape),
            (BASE.personName, SH.path, SDO.name),
            (BASE.personName, SH.name, Literal("Name", lang="en")),
            (BASE.personName, SH.name, Literal("Nombre", lang="es")),
            (BASE.personName, SH.minLength, Literal(2)),
            (BASE.personName, SH.minCount, Literal(1)),
            (BASE.personName, SH.severity, SH.Violation),
        ]
    )
    expected_ttl.extend(
        "sh:or ( [ sh:datatype xsd:string ] [ sh:datatype rdf:langString ] ) ;"
    )
    return ps


@pytest.fixture(scope="module")
def ageMax_ps():
    ps = PropertyStatement()
    ps.add_shape("#Person")
    ps.add_property("schema:age")
    ps.add_label("en", "Age")
    ps.add_valueNodeType("literal")
    ps.add_valueDataType("xsd:decimal")
    ps.add_valueConstraintType("maximum")
    ps.add_valueConstraint("150")
    ps.add_severity("Violation")
    expected_triples.extend(
        [
            (BASE.Person, SH.property, BASE.personAge),
            (BASE.personAge, RDF.type, SH.PropertyShape),
            (BASE.personAge, SH.path, SDO.age),
            (BASE.personAge, SH.name, Literal("Age", lang="en")),
            (BASE.personAge, SH.maxInclusive, Literal(150)),
            (BASE.personAge, SH.severity, SH.Violation),
        ]
    )
    return ps


@pytest.fixture(scope="module")
def ageMin_ps():
    ps = PropertyStatement()
    ps.add_shape("#Person")
    ps.add_property("schema:age")
    ps.add_label("en", "Age")
    ps.add_valueNodeType("literal")
    ps.add_valueDataType("xsd:decimal")
    ps.add_valueConstraintType("minimum")
    ps.add_valueConstraint("18")
    ps.add_severity("Violation")
    expected_triples.extend(
        [
            (BASE.personAge, SH.minInclusive, Literal(18)),
        ]
    )
    return ps


def description_ps():
    ps = PropertyStatement()
    ps.add_shape("#Person")
    ps.add_property("schema:description")
    ps.add_valueNodeType("literal")
    ps.add_valueDataType("xsd:string")
    ps.add_valueConstraintType("maxLength")
    ps.add_valueConstraint("1024")
    ps.add_mandatory(False)
    ps.add_repeatable(False)
    ps.add_severity("Violation")
    expected_triples.extend(
        [
            (BASE.Person, SH.property, BASE.personDescription),
            (BASE.personDescription, RDF.type, SH.PropertyShape),
            (BASE.personDescription, SH.path, SDO.description),
            (BASE.personDescription, SH.datatype, XSD.string),
            (BASE.personDescription, SH.maxLength, Literal(1024)),
            (BASE.personDescription, SH.maxCount, Literal(1)),
            (BASE.personDescription, SH.severity, SH.Violation),
        ]
    )
    return ps


@pytest.fixture(scope="module")
def person_type_ps():
    ps = PropertyStatement()
    ps.add_shape("#Person")
    ps.add_property("rdf:type")
    ps.add_label("en", "Type")
    ps.add_mandatory(True)
    ps.add_repeatable(False)
    ps.add_valueNodeType("IRI")
    ps.add_valueConstraint("schema:Person")
    ps.add_severity("Violation")
    expected_triples.extend(
        [
            (BASE.Person, SH_class, SDO.Person),
        ]
    )
    return ps


@pytest.fixture(scope="module")
def contact_ps():
    ps = PropertyStatement()
    ps.add_shape("#Person")
    ps.add_property("schema:email")
    ps.add_property("schema:address")
    ps.add_label("en", "Contact")
    ps.add_mandatory(True)
    ps.add_repeatable(True)
    ps.add_severity("Violation")
    expected_triples.extend(
        [
            (BASE.personContact_schema_email_opt, RDF.type, SH.PropertyShape),
            (BASE.personContact_schema_email_opt, SH.path, SDO.email),
            (BASE.personContact_schema_email_opt, SH.minCount, Literal(1)),
            (BASE.personContact_schema_email_opt, SH.severity, SH.Violation),
            (BASE.personContact_schema_address_opt, RDF.type, SH.PropertyShape),
            (BASE.personContact_schema_address_opt, SH.path, SDO.address),
            (BASE.personContact_schema_address_opt, SH.minCount, Literal(1)),
            (BASE.personContact_schema_address_opt, SH.severity, SH.Violation),
        ]
    )
    expected_ttl.extend(
        "sh:or ( <personContact_schema_email_opt> <personContact_schema_address_opt> ) ;"
    )
    return ps


@pytest.fixture(scope="module")
def email_ps():
    ps = PropertyStatement()
    ps.add_shape("#Person")
    ps.add_property("schema:email")
    ps.add_label("en", "Email")
    ps.add_mandatory(False)
    ps.add_repeatable(True)
    ps.add_valueNodeType("literal")
    ps.add_valueDataType("xsd:string")
    ps.add_valueConstraint("/.+@.+/")
    ps.add_valueConstraintType("pattern")
    ps.add_severity("Warning")
    expected_triples.extend(
        [
            (BASE.Person, SH.property, BASE.personEmail),
            (BASE.personEmail, RDF.type, SH.PropertyShape),
            (BASE.personEmail, SH.path, SDO.email),
            (BASE.personEmail, SH.name, Literal("Email", lang="en")),
            (BASE.personEmail, SH.nodeKind, SH.Literal),
            (BASE.personEmail, SH.pattern, Literal("/.+@.+/")),
            (BASE.personEmail, SH.severity, SH.Warning),
        ]
    )
    return ps


@pytest.fixture(scope="module")
def email_length_ps():
    ps = PropertyStatement()
    ps.add_shape("#Person")
    ps.add_property("schema:email")
    ps.add_label("en", "Email Length")
    ps.add_valueNodeType("literal")
    ps.add_valueDataType("xsd:string")
    ps.add_valueConstraint("6..1024")
    ps.add_valueConstraintType("lengthrange")
    ps.add_severity("Warning")
    expected_triples.extend(
        [
            (BASE.Person, SH.property, BASE.personEmailLength),
            (BASE.personEmailLength, RDF.type, SH.PropertyShape),
            (BASE.personEmailLength, SH.path, SDO.email),
            (BASE.personEmailLength, SH.name, Literal("Email Length", lang="en")),
            (BASE.personEmailLength, SH.nodeKind, SH.Literal),
            (BASE.personEmailLength, SH.minLength, Literal(6)),
            (BASE.personEmailLength, SH.maxLength, Literal(1024)),
            (BASE.personEmailLength, SH.severity, SH.Warning),
        ]
    )
    return ps


@pytest.fixture(scope="module")
def address_ps():
    ps = PropertyStatement()
    ps.add_shape("#Person")
    ps.add_property("schema:address")
    ps.add_label("en", "Address")
    ps.add_mandatory(False)
    ps.add_repeatable(True)
    ps.add_valueNodeType("iri")
    ps.add_valueNodeType("BNode")
    ps.add_valueShape("#Address")
    ps.add_severity("Warning")
    expected_triples.extend(
        [
            (BASE.Person, SH.property, BASE.personAddress),
            (BASE.personAddress, RDF.type, SH.PropertyShape),
            (BASE.personAddress, SH.path, SDO.address),
            (BASE.personAddress, SH.name, Literal("Address", lang="en")),
            (BASE.personAddress, SH.nodeKind, SH.BlankNodeOrIRI),
            (BASE.personAddress, SH.node, BASE.Address),
            (BASE.personAddress, SH.severity, SH.Warning),
        ]
    )
    return ps


@pytest.fixture(scope="module")
def address_type_ps():
    ps = PropertyStatement()
    ps.add_shape("#Address")
    ps.add_property("rdf:type")
    ps.add_label("en", "Type")
    ps.add_mandatory(True)
    ps.add_repeatable(False)
    ps.add_valueNodeType("iri")
    ps.add_valueConstraint("schema:PostalAddress")
    ps.add_severity("Violation")
    expected_triples.extend(
        [
            (BASE.Address, SH_class, SDO.PostalAddress),
        ]
    )
    return ps


@pytest.fixture(scope="module")
def address_option_ps():
    ps = PropertyStatement()
    ps.add_shape("#Address")
    ps.add_property("schema:contactOption")
    ps.add_label("en", "Contact Option")
    ps.add_mandatory(False)
    ps.add_repeatable(True)
    ps.add_valueNodeType("iri")
    ps.add_valueConstraint("schema:HearingImpairedSupported")
    ps.add_valueConstraint("schema:TollFree")
    ps.add_severity("Violation")
    expected_triples.extend(
        [
            (BASE.Address, SH.property, BASE.addressContactOption),
            (BASE.addressContactOption, RDF.type, SH.PropertyShape),
            (BASE.addressContactOption, SH.path, SDO.contactOption),
            (
                BASE.addressContactOption,
                SH.name,
                Literal("Contact Option", lang="en"),
            ),
            (BASE.addressContactOption, SH.nodeKind, SH.IRI),
        ]
    )
    expected_ttl.extend("sh:in ( schema:HearingImpairedSupported schema:TollFree ) ;")
    return ps


@pytest.fixture(scope="module")
def person_shapeInfo():
    shapeInfo = ShapeInfo(
        label={"en": "Person shape"},
        comment={"en": "A shape for tests"},
        targets={"class": "schema:Person"},
        mandatory=True,
        severity="warning",
        closed=True,
        ignoreProps=["rdf:type"],
    )
    expected_triples.extend(
        [
            (BASE.Person, RDF.type, SH.NodeShape),
            (BASE.Person, SH.name, Literal("Person shape", lang="en")),
            (BASE.Person, SH.description, Literal("A shape for tests", lang="en")),
            (BASE.Person, SH.targetClass, schema.Person),
            (BASE.Person, SH.closed, Literal("True", datatype=XSD.boolean)),
        ]
    )
    expected_ttl.extend("sh:ignoredProperties ( rdf:type ) ;")
    return shapeInfo


@pytest.fixture(scope="module")
def address_shapeInfo():
    shapeInfo = ShapeInfo(
        label={"en": "Address shape"},
        comment={"en": "A shape for tests"},
        targets={"ObjectsOf": "schema:address", "class": "schema:PostalAddress"},
        mandatory=False,
        ignoreProps=[],
        severity="Warning",
    )
    expected_triples.extend(
        [
            (BASE.Address, RDF.type, SH.NodeShape),
            (BASE.Address, SH.name, Literal("Address shape", lang="en")),
            (BASE.Address, SH.description, Literal("A shape for tests", lang="en")),
            (BASE.Address, SH.targetObjectsOf, SDO.address),
            (BASE.Address, SH_class, SDO.PostalAddress),
        ]
    )
    return shapeInfo


@pytest.fixture(scope="module")
def simple_ap(
    person_shapeInfo,
    name_ps,
    ageMin_ps,
    ageMax_ps,
    person_type_ps,
    contact_ps,
    email_ps,
    email_length_ps,
    address_ps,
    address_shapeInfo,
    address_type_ps,
    address_option_ps,
):
    ap = AP()
    ap.load_namespaces("tests/TestData/namespaces.csv")
    ap.add_metadata("dct:title", "Test application profile")
    ap.add_metadata("dct:date", "2021-08-09")
    ap.add_shapeInfo("#Person", person_shapeInfo)
    ap.add_propertyStatement(person_type_ps)
    ap.add_propertyStatement(name_ps)
    ap.add_propertyStatement(ageMax_ps)
    ap.add_propertyStatement(ageMin_ps)
    ap.add_propertyStatement(contact_ps)
    ap.add_propertyStatement(email_ps)
    ap.add_propertyStatement(email_length_ps)
    ap.add_propertyStatement(address_ps)
    ap.add_shapeInfo("#Address", address_shapeInfo)
    ap.add_propertyStatement(address_type_ps)
    ap.add_propertyStatement(address_option_ps)
    expected_ttl.extend(
        [
            "@base <http://example.org/shapes#> .",
            "@prefix base: <http://example.org/shapes#> .",
            "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
            "@prefix schema: <https://schema.org/> .",
            "@prefix sh: <http://www.w3.org/ns/shacl#> .",
            "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
        ]
    )
    return ap


def test_list2RDFList():
    g = Graph()
    list = [1, 2, 3]
    node_type = "literal"
    namespaces = {}
    start_node = list2RDFList(g, list, node_type, namespaces)
    g.add((SDO.name, SH_in, start_node))
    expected_ttl = "<https://schema.org/name> ns1:in ( 1 2 3 )"
    assert expected_ttl in g.serialize(format="turtle")
    g = Graph()
    list = ["sdo:address", "sdo:email", "sdo:contactOption"]
    node_type = "anyURI"
    namespaces = {"sdo": "https://schema.org/"}
    start_node = list2RDFList(g, list, node_type, namespaces)
    g.add((URIRef("#cont"), SH_or, start_node))
    expected_ttl = "<#cont> ns1:or ( <https://schema.org/address> <https://schema.org/email> <https://schema.org/contactOption> )"
    assert expected_ttl in g.serialize(format="turtle")
    list = [BNode(1), BNode(2), BNode(3)]
    node_type = "bnode"
    start_node = list2RDFList(g, list, node_type, {})
    g.add((URIRef("#blank"), SH_or, start_node))
    expected_ttl = "<#blank> ns1:or ( [ ] [ ] [ ] )"
    assert expected_ttl in g.serialize(format="turtle")


def test_make_property_shape_name():
    ps = PropertyStatement()
    name = make_property_shape_name(ps)
    assert type(name) == str
    ps.add_label("fr", "Coleur")
    name = make_property_shape_name(ps)
    assert name == "_Coleur"
    ps.add_label("en-US", "Color Property")
    name = make_property_shape_name(ps)
    assert name == "_ColorProperty"
    ps.add_label("en", "Colour Property")
    name = make_property_shape_name(ps)
    assert name == "_ColourProperty"


def test_ap2shaclInit(simple_ap):
    converter = AP2SHACLConverter(simple_ap)
    #    converter.dump_shacl()
    assert type(converter.ap) == AP
    assert converter.ap.metadata["dct:title"] == "Test application profile"
    assert "dct" in converter.ap.namespaces.keys()
    assert "rdf" in converter.ap.namespaces.keys()
    assert "sh" in converter.ap.namespaces.keys()
    assert len(converter.ap.propertyStatements) == 10
    assert len(converter.ap.shapeInfo) == 2
    assert type(converter.sg) == Graph


def test_convert_AP_SHACL(simple_ap):
    converter = AP2SHACLConverter(simple_ap)
    converter.convert_AP_SHACL()
    converter.dump_shacl()
    all_ns = [n for n in converter.sg.namespace_manager.namespaces()]
    assert ("schema", URIRef("https://schema.org/")) in all_ns
    assert ("sh", URIRef("http://www.w3.org/ns/shacl#")) in all_ns
    assert ("base", URIRef("http://example.org/shapes#")) in all_ns
    for t in expected_triples:
        assert t in converter.sg
    ttl = converter.sg.serialize(format="turtle")
    for s in expected_ttl:
        assert s in ttl


def test_str2URIRef():
    ns = {"rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"}
    string = "rdf:label"
    uri = str2URIRef(ns, string)
    assert uri == RDF.label
    ns = {"base": "https://schema.org/"}
    string = "name"
    uri = str2URIRef(ns, string)
    assert uri == SDO.name
    string = "https://schema.org/description"
    ns = {}
    uri = str2URIRef(ns, string)
    assert uri == URIRef(string)
    uri = str2URIRef({}, "name")
    assert uri == URIRef("http://example.org/name")
    ns = {"base": "http://example.org/terms#"}
    uri = str2URIRef(ns, "#name")  # make sure the extra # is stripped
    assert uri == URIRef("http://example.org/terms#name")
    with pytest.raises(TypeError) as e:
        uri = str2URIRef([], "name")
    assert str(e.value) == "Namespaces should be a dictionary."
    with pytest.raises(TypeError) as e:
        uri = str2URIRef({}, 42)
    assert str(e.value) == "Value to convert should be a non-empty string."
    with pytest.raises(TypeError) as e:
        uri = str2URIRef({}, "")
    assert str(e.value) == "Value to convert should be a non-empty string."
    with pytest.raises(ValueError) as e:
        uri = str2URIRef({}, "ns:name")
    assert str(e.value) == "Prefix ns not in namespace list."


def test_convertNodeKind():
    assert convert_nodeKind(["IrI"]) == SH.IRI
    assert convert_nodeKind(["bNode"]) == SH.BlankNode
    assert convert_nodeKind(["literal"]) == SH.Literal
    assert convert_nodeKind(["IrI", "BNode"]) == SH.BlankNodeOrIRI
    assert convert_nodeKind(["IrI", "Literal"]) == SH.IRIOrLiteral
    assert convert_nodeKind(["bnode", "Literal"]) == SH.BlankNodeOrLiteral
    assert convert_nodeKind(["iri", "bnode", "literal"]) == None
    with pytest.raises(TypeError) as e:
        convert_nodeKind("IRI")
    assert str(e.value) == "Node_types must be a list."
    with pytest.raises(ValueError) as e:
        convert_nodeKind(["wrong"])
    assert str(e.value) == "Node type unknown."
