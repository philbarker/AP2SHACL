import pytest
from AP2SHACL import (
    AP2SHACLConverter,
    make_property_shape_name,
    list2RDFList,
    AP,
    PropertyStatement,
)
from rdflib import Graph, URIRef, Literal, BNode, Namespace, RDF, RDFS, SH

schema = Namespace("https://schema.org/")
SDO = Namespace("https://schema.org/")  # "httpS"
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
BASE = Namespace("http://example.org/shapes#")
# avoid stoopid conflicts python keywords
SH_in = URIRef("http://www.w3.org/ns/shacl#in")
SH_or = URIRef("http://www.w3.org/ns/shacl#or")
SH_class = URIRef("http://www.w3.org/ns/shacl#class")
expected_triples = []


@pytest.fixture(scope="module")
def name_ps():
    ps = PropertyStatement()
    ps.add_shape("#Person")
    ps.add_property("schema:name")
    ps.add_label("en", "Name")
    ps.add_label("es", "Nombre")
    ps.add_valueNodeType("literal")
    ps.add_valueDataType("xsd:string")
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
            (BASE.personName, SH.datatype, XSD.string),
            (BASE.personName, SH.minLength, Literal(2)),
            (BASE.personName, SH.minCount, Literal(1)),
            (BASE.personName, SH.severity, SH.Violation),
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
    ps.add_valueNodeType("iri")
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
            (BASE.Person, SH_or, BNode("personContact_schema_email_opt")),
            (
                BNode("personContact_schema_email_opt"),
                RDF.first,
                BASE.personContact_schema_email_opt,
            ),
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
            (
                BASE.addressContactOption,
                SH_in,
                BNode("schema_HearingImpairedSupported"),
            ),
            (
                BNode("schema_HearingImpairedSupported"),
                RDF.first,
                SDO.HearingImpairedSupported,
            ),
        ]
    )
    return ps


@pytest.fixture(scope="module")
def person_shapeInfo():
    shapeInfo = {
        "label": "Person shape",
        "comment": "A shape for tests",
        "target": "schema:Person",
        "targetType": "class",
        "mandatory": True,
        "severity": "Warning",
        "closed": True,
        "ignoreProps": "rdf:type",
    }
    expected_triples.extend(
        [
            (BASE.Person, RDF.type, SH.NodeShape),
            (BASE.Person, SH.name, Literal("Person shape", lang="en")),
            (BASE.Person, SH.description, Literal("A shape for tests", lang="en")),
            (BASE.Person, SH.targetClass, schema.Person),
            (BASE.Person, SH.ignoredProperties, RDF.type),
            (BASE.Person, SH.closed, Literal("True", datatype=XSD.boolean)),
        ]
    )
    return shapeInfo


@pytest.fixture(scope="module")
def address_shapeInfo():
    shapeInfo = {
        "label": "Address shape",
        "comment": "A shape for tests",
        "target": "schema:address",
        "targetType": "ObjectsOf",
        "mandatory": False,
        "ignoreProps": "",
        "severity": "Warning",
    }
    expected_triples.extend(
        [
            (BASE.Address, RDF.type, SH.NodeShape),
            (BASE.Address, SH.name, Literal("Address shape", lang="en")),
            (BASE.Address, SH.description, Literal("A shape for tests", lang="en")),
            (BASE.Address, SH.targetObjectsOf, SDO.address),
        ]
    )
    return shapeInfo


@pytest.fixture(scope="module")
def simple_ap(
    person_shapeInfo,
    name_ps,
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
    ap.add_propertyStatement(contact_ps)
    ap.add_propertyStatement(email_ps)
    ap.add_propertyStatement(email_length_ps)
    ap.add_propertyStatement(address_ps)
    ap.add_shapeInfo("#Address", address_shapeInfo)
    ap.add_propertyStatement(address_type_ps)
    ap.add_propertyStatement(address_option_ps)

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
    assert len(converter.ap.propertyStatements) == 8
    assert len(converter.ap.shapeInfo) == 2
    assert type(converter.sg) == Graph


def test_convert_AP_SHACL(simple_ap):
    converter = AP2SHACLConverter(simple_ap)
    converter.convert_AP_SHACL()
#    converter.dump_shacl()
    all_ns = [n for n in converter.sg.namespace_manager.namespaces()]
    assert ("schema", URIRef("https://schema.org/")) in all_ns
    assert ("sh", URIRef("http://www.w3.org/ns/shacl#")) in all_ns
    assert ("base", URIRef("http://example.org/shapes#")) in all_ns
    for t in expected_triples:
        assert t in converter.sg
