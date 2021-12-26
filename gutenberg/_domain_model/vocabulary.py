"""Module to hold relevant parts of the RDF vocabulary used in Project
Gutenberg."""


import rdflib.namespace


DCTERMS = rdflib.namespace.DCTERMS
PGTERMS = rdflib.namespace.Namespace(r'http://www.gutenberg.org/2009/pgterms/')
RDFTERMS = rdflib.namespace.RDF
