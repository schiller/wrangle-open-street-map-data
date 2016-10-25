#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import os
import json

INPUT_PATH = 'input/rio-de-janeiro_brazil.osm'
# INPUT_PATH = 'input/sample-100.osm'
# INPUT_PATH = 'input/sample-1000.osm'
OUTPUT_DIR = 'output'
OUTPUT_PATH_ST_TYPES = '{}/street_types.json'.format(OUTPUT_DIR)
OUTPUT_PATH_UPDATED_ST_NAMES = '{}/updated_st_names.json'.format(OUTPUT_DIR)

street_type_re = re.compile(r'^\S+\.?(\b)?', re.IGNORECASE)

expected = ["Acesso", "Alameda", "Avenida", "Beco", "Boulevard", "Caminho",
    "Campo", u"Condomínio", "Estrada", "Ladeira", "Largo", "Parque", u"Praça",
    "Praia", "Rodovia", "Rua", "Travessa", "Via"]

mapping = { "Av": "Avenida",
            "Av.": "Avenida",
            "Est.": "Estrada",
            "Estr.": "Estrada",
            "estrada": "Estrada",
            "Pca": u"Praça",
            "Praca": u"Praça",
            u"Pça": u"Praça",
            u"Pça.": u"Praça",
            "R.": "Rua",
            "RUA": "Rua",
            "rua": "Rua",
            "Ruas": "Rua",
            "Rue": "Rua",
            "Rod.": "Rodovia",
            "Trav": "Travessa" }
            


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types

def update_name(name, mapping):
    m = street_type_re.search(name)
    street_type = m.group()
    if street_type in mapping:
        name = street_type_re.sub(mapping[street_type], name)
    return name

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

def print_street_types():
    st_types = audit(INPUT_PATH)

    try: 
        os.makedirs(OUTPUT_DIR)
    except OSError:
        if not os.path.isdir(OUTPUT_DIR):
            raise

    with open(OUTPUT_PATH_ST_TYPES, 'wb') as output:
        output.write(json.dumps(st_types, indent=2, cls=SetEncoder))

    pprint.pprint(dict(st_types))
    return st_types


def update_street_names(st_types):
    names = defaultdict(dict)

    for st_type, ways in st_types.iteritems():
            for name in ways:
                better_name = update_name(name, mapping)
                names[st_type][name] = better_name

    with open(OUTPUT_PATH_UPDATED_ST_NAMES, 'wb') as output:
        output.write(json.dumps(names, indent=2))


if __name__ == '__main__':
    st_types = print_street_types()
    update_street_names(st_types)