#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

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

# in portuguese the street type is the first word of the street address
street_type_re = re.compile(r'^\S+\.?(\b)?', re.IGNORECASE)

def update_street_type(name):
    """Updates street type according to the mapping"""
    m = street_type_re.search(name)
    if m:
        street_type = m.group()
        if street_type in mapping:
            name = street_type_re.sub(mapping[street_type], name)
    return name

def handle_address(node, parts, v):
    """Updates the address field of the element's dict"""
    if len(parts) > 2:
        return node
    if parts[1] == 'street':
        v = update_street_type(v)
    if 'address' not in node:
        node['address'] = dict()
    node['address'][parts[1]] = v