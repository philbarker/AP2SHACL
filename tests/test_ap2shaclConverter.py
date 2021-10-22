import pytest
from AP import AP, PropertyStatement
from AP2SHACL import AP2SHACLConverter, make_property_shape_id, list2RDFList
from rdflib import Graph, URIRef, Literal, BNode, Namespace, RDF, RDFS, SH

schema = Namespace("https://schema.org/")
SDO = Namespace("https://schema.org/")  # "httpS"
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
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
    ps.add_valueNodeType("Literal")
    ps.add_valueDataType("xsd:string")
    ps.add_valueConstraintType("minLength")
    ps.add_valueConstraint("2")
    ps.add_mandatory(True)
    ps.add_repeatable(True)
    ps.add_severity("Violation")
    expected_triples.extend(
        [
            (URIRef("#Person"), SH.property, URIRef("#personName_value")),
            (URIRef("#personName_value"), RDF.type, SH.PropertyShape),
            (URIRef("#personName_value"), SH.path, SDO.name),
            (URIRef("#personName_value"), SH.name, Literal("Name", lang="en")),
            (URIRef("#personName_value"), SH.name, Literal("Nombre", lang="es")),
            (URIRef("#personName_value"), SH.datatype, XSD.string),
            (URIRef("#personName_value"), SH.minLength, Literal(2)),
            (URIRef("#Person"), SH.property, URIRef("#personName_count")),
            (URIRef("#personName_count"), RDF.type, SH.PropertyShape),
            (URIRef("#personName_count"), SH.path, SDO.name),
            (URIRef("#personName_count"), SH.minCount, Literal(1)),
            (URIRef("#personName_count"), SH.severity, SH.Violation),
            (URIRef("#personName_value"), SH.severity, SH.Violation),
        ]
    )
    return ps


def description_ps():
    ps = PropertyStatement()
    ps.add_shape("#Person")
    ps.add_property("schema:description")
    ps.add_valueNodeType("Literal")
    ps.add_valueDataType("xsd:string")
    ps.add_valueConstraintType("maxLength")
    ps.add_valueConstraint("1024")
    ps.add_mandatory(False)
    ps.add_repeatable(False)
    ps.add_severity("Violation")
    expected_triples.extend(
        [
            (URIRef("#Person"), SH.property, URIRef("#personDescription_value")),
            (URIRef("#personDescription_value"), RDF.type, SH.PropertyShape),
            (URIRef("#personDescription_value"), SH.path, SDO.description),
            (URIRef("#personDescription_value"), SH.datatype, XSD.string),
            (URIRef("#personDescription_value"), SH.maxLength, Literal(1024)),
            (URIRef("#Person"), SH.property, URIRef("#personDescription_count")),
            (URIRef("#personDescription_count"), RDF.type, SH.PropertyShape),
            (URIRef("#personDescription_count"), SH.path, SDO.description),
            (URIRef("#personDescription_count"), SH.maxCount, Literal(1)),
            (URIRef("#personDescription_count"), SH.severity, SH.Violation),
            (URIRef("#personDescription_value"), SH.severity, SH.Violation),
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
            (URIRef("#Person"), SH_class, SDO.Person),
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
            (URIRef("#Person"), SH_or, BNode("personContact-schema-email-opt")),
            (
                BNode("personContact-schema-email-opt"),
                RDF.first,
                URIRef("#personContact-schema-email-opt"),
            ),
            (URIRef("#personContact-schema-email-opt"), RDF.type, SH.PropertyShape),
            (URIRef("#personContact-schema-email-opt"), SH.path, SDO.email),
            (URIRef("#personContact-schema-email-opt"), SH.minCount, Literal(1)),
            (URIRef("#personContact-schema-email-opt"), SH.severity, SH.Violation),
            (URIRef("#personContact-schema-address-opt"), RDF.type, SH.PropertyShape),
            (URIRef("#personContact-schema-address-opt"), SH.path, SDO.address),
            (URIRef("#personContact-schema-address-opt"), SH.minCount, Literal(1)),
            (URIRef("#personContact-schema-address-opt"), SH.severity, SH.Violation),
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
    ps.add_valueNodeType("Literal")
    ps.add_valueDataType("xsd:string")
    ps.add_valueConstraint("/.+@.+/")
    ps.add_valueConstraintType("pattern")
    ps.add_severity("Warning")
    expected_triples.extend(
        [
            (URIRef("#Person"), SH.property, URIRef("#personEmail_value")),
            (URIRef("#personEmail_value"), RDF.type, SH.PropertyShape),
            (URIRef("#personEmail_value"), SH.path, SDO.email),
            (URIRef("#personEmail_value"), SH.name, Literal("Email", lang="en")),
            (URIRef("#personEmail_value"), SH.nodeKind, SH.Literal),
            (URIRef("#personEmail_value"), SH.pattern, Literal("/.+@.+/")),
            (URIRef("#personEmail_value"), SH.severity, SH.Warning),
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
    ps.add_valueNodeType("IRI")
    ps.add_valueNodeType("BNode")
    ps.add_valueShape("#Address")
    ps.add_severity("Warning")
    expected_triples.extend(
        [
            (URIRef("#Person"), SH.property, URIRef("#personAddress_value")),
            (URIRef("#personAddress_value"), RDF.type, SH.PropertyShape),
            (URIRef("#personAddress_value"), SH.path, SDO.address),
            (URIRef("#personAddress_value"), SH.name, Literal("Address", lang="en")),
            (URIRef("#personAddress_value"), SH.nodeKind, SH.BlankNodeOrIRI),
            (URIRef("#personAddress_value"), SH.node, URIRef("#Address")),
            (URIRef("#personAddress_value"), SH.severity, SH.Warning),
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
    ps.add_valueNodeType("IRI")
    ps.add_valueConstraint("schema:PostalAddress")
    ps.add_severity("Violation")
    expected_triples.extend(
        [
            (URIRef("#Address"), SH_class, SDO.PostalAddress),
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
    ps.add_valueNodeType("IRI")
    ps.add_valueConstraint("schema:HearingImpairedSupported")
    ps.add_valueConstraint("schema:TollFree")
    ps.add_severity("Violation")
    expected_triples.extend(
        [
            (URIRef("#Address"), SH.property, URIRef("#addressContactOption_value")),
            (URIRef("#addressContactOption_value"), RDF.type, SH.PropertyShape),
            (URIRef("#addressContactOption_value"), SH.path, SDO.contactOption),
            (
                URIRef("#addressContactOption_value"),
                SH.name,
                Literal("Contact Option", lang="en"),
            ),
            (URIRef("#addressContactOption_value"), SH.nodeKind, SH.IRI),
            (
                URIRef("#addressContactOption_value"),
                SH_in,
                BNode("schema-HearingImpairedSupported"),
            ),
            (
                BNode("schema-HearingImpairedSupported"),
                RDF.first,
                URIRef("https://schema.org/HearingImpairedSupported"),
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
        "properties": ["name", "contact", "description"],
    }
    expected_triples.extend(
        [
            (URIRef("#Person"), RDF.type, SH.NodeShape),
            (URIRef("#Person"), SH.name, Literal("Person shape", lang="en")),
            (URIRef("#Person"), SH.description, Literal("A shape for tests", lang="en")),
            (URIRef("#Person"), SH.targetClass, schema.Person),
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
        "severity": "Warning",
        "properties": [],
    }
    expected_triples.extend(
        [
            (URIRef("#Address"), RDF.type, SH.NodeShape),
            (URIRef("#Address"), SH.name, Literal("Address shape", lang="en")),
            (URIRef("#Address"), SH.description, Literal("A shape for tests", lang="en")),
            (URIRef("#Address"), SH.targetObjectsOf, SDO.address),
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
    ap.add_propertyStatement(address_ps)
    ap.add_shapeInfo("#Address", address_shapeInfo)
    ap.add_propertyStatement(address_type_ps)
    ap.add_propertyStatement(address_option_ps)

    return ap


def test_list2RDFList():
    g = Graph()
    list = [1, 2, 3]
    node_type = "Literal"
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


def test_make_property_shape_id():
    ps = PropertyStatement()
    id = make_property_shape_id(ps)
    assert type(id) == URIRef
    ps.add_label("fr", "Coleur")
    id = make_property_shape_id(ps)
    assert id == URIRef("#_Coleur")
    ps.add_label("en-US", "Color Property")
    id = make_property_shape_id(ps)
    assert id == URIRef("#_ColorProperty")
    ps.add_label("en", "Colour Property")
    id = make_property_shape_id(ps)
    assert id == URIRef("#_ColourProperty")


def test_ap2shaclInit(simple_ap):
    converter = AP2SHACLConverter(simple_ap)
    converter.dump_shacl()
    assert type(converter.ap) == AP
    assert converter.ap.metadata["dct:title"] == "Test application profile"
    assert "dct" in converter.ap.namespaces.keys()
    assert "rdf" in converter.ap.namespaces.keys()
    assert "sh" in converter.ap.namespaces.keys()
    assert len(converter.ap.propertyStatements) == 7
    assert len(converter.ap.shapeInfo) == 2
    assert type(converter.sg) == Graph

def test_convert_AP_SHACL(simple_ap):
    converter = AP2SHACLConverter(simple_ap)
    converter.convert_AP_SHACL()
    all_ns = [n for n in converter.sg.namespace_manager.namespaces()]
    assert ("schema", URIRef("https://schema.org/")) in all_ns
    assert ("sh", URIRef("http://www.w3.org/ns/shacl#")) in all_ns
    assert ("base", URIRef("http://example.org/")) in all_ns
    for t in expected_triples:
        assert t in converter.sg
