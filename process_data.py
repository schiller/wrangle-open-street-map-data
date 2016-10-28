#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import re
import codecs
import json
import os
from process_address import handle_address
from process_phones import handle_phone

INPUT_DIR = 'input'
INPUT_FILE = 'rio-de-janeiro_brazil.osm'
# INPUT_FILE = 'sample-100.osm'
# INPUT_FILE = 'sample-1000.osm'
INPUT_PATH = '{0}/{1}'.format(INPUT_DIR, INPUT_FILE)
OUTPUT_DIR = 'output'
OUTPUT_PATH = '{0}/{1}.json'.format(OUTPUT_DIR, INPUT_FILE)

CREATED = ["version", "changeset", "timestamp", "user", "uid"]

problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


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


def shape_tag(node, tag):
    k = tag.attrib.get('k')
    v = tag.attrib.get('v')

    if problemchars.search(k):
        return node
    elif ':' in k:
        parts = k.split(':')
        if parts[0] == 'addr':
            node = handle_address(node, parts, v)
        else:
            k = '_'.join(parts)
            node[k] = v
    else:
        if k == 'type':
            k = 'type_tag'
        if k == 'phone':
            v = handle_phone(v)
        node[k] = v
    return node


def handle_bicycle_parking_capacity(node):
    """Converts bicycle_parking capacity to int."""
    if ('amenity' in node) and (node['amenity'] == 'bicycle_parking'):
        if 'capacity' in node:
            try:
                node['capacity'] = int(node['capacity'])
            except ValueError:
                node.pop('capacity')


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

        handle_bicycle_parking_capacity(node)

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


if __name__ == '__main__':
    process_map()