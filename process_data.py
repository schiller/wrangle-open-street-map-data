#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import re
import codecs
import json
import os

INPUT_DIR = 'input'
INPUT_FILE = 'rio-de-janeiro_brazil.osm'
# INPUT_FILE = 'sample-100.osm'
# INPUT_FILE = 'sample-1000.osm'
INPUT_PATH = '{0}/{1}'.format(INPUT_DIR, INPUT_FILE)
OUTPUT_DIR = 'output'
OUTPUT_PATH = '{0}/{1}.json'.format(OUTPUT_DIR, INPUT_FILE)

CREATED = ["version", "changeset", "timestamp", "user", "uid"]

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

problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
street_type_re = re.compile(r'^\S+\.?(\b)?', re.IGNORECASE)


def shape_attribute(node, k, v):
    if k in CREATED:
        if 'created' not in node:
            node['created'] = dict()
        node['created'][k] = v
    elif (k == 'lat') or (k == 'lon'):
        if 'pos' not in node:
            node['pos'] = list()
        if k == 'lon':
            node['pos'].insert(0, float(v))                
        elif k == 'lat':
            node['pos'].append(float(v))
    else:
        node[k] = v
    return node


def shape_nd(node, tag):
    if 'node_refs' not in node:
        node['node_refs'] = list()
    node['node_refs'].append(tag.attrib.get('ref'))
    return node
            

def update_street_type(name):
    m = street_type_re.search(name)
    if m:
        street_type = m.group()
        if street_type in mapping:
            name = street_type_re.sub(mapping[street_type], name)
    return name


def shape_tag(node, tag):
    k = tag.attrib.get('k')
    v = tag.attrib.get('v')

    if problemchars.search(k):
        return node
    elif ':' in k:
        parts = k.split(':')
        if parts[0] == 'addr':
            if len(parts) > 2:
                return node
            if parts[1] == 'street':
                v = update_street_type(v)
            if 'address' not in node:
                node['address'] = dict()
            node['address'][parts[1]] = v
        else:
            k = '_'.join(parts)
            node[k] = v
    else:
        if k == 'type':
            k = 'type_tag'
        node[k] = v
    return node


def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        node['type'] = element.tag

        for key, value in element.attrib.items():
            shape_attribute(node, key, value)

        for tag in element.iter('nd'):
            shape_nd(node, tag)

        for tag in element.iter('tag'):
            shape_tag(node, tag)

        return node
    else:
        return None


def process_map(pretty = False):
    try: 
        os.makedirs(OUTPUT_DIR)
    except OSError:
        if not os.path.isdir(OUTPUT_DIR):
            raise

    with codecs.open(OUTPUT_PATH, 'wb', 'utf-8') as fo:
        for _, element in ET.iterparse(INPUT_PATH):
            el = shape_element(element)
            if el:
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")


process_map()