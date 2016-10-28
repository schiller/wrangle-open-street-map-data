#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import re
import pprint
import os
import json

INPUT_PATH = 'input/rio-de-janeiro_brazil.osm'
# INPUT_PATH = 'input/sample-100.osm'
# INPUT_PATH = 'input/sample-1000.osm'
OUTPUT_DIR = 'output'
# OUTPUT_PATH_FORMATS = '{}/phone_formats.json'.format(OUTPUT_DIR)
OUTPUT_PATH_FORMATS = '{}/phone_formats_updated.json'.format(OUTPUT_DIR)
OUTPUT_PATH_PROBLEM = '{}/problem_phones.json'.format(OUTPUT_DIR)


# +55 99 99999999
phone_ok_re = re.compile(r'^\+55\s\d{2}\s\d{8,9}$')
# 0800 999 9999
phone_0800_ok_re = re.compile(r'^0800\s\d{3}\s\d{4}$')
# 55-99-9-99999999
wrong_separators_re = re.compile(r'^\D*55\D*\d{2}\D*(\d\D?)?\d{4}\D?\d{4}$')
# +55-99-0800-999-9999
wrong_separators_0800_re = re.compile(r'^\D*(55)?\D*(\d{2})?\D*0800\D?\d{3}\D?\d\D?\d{3}$')
# missing +55 (Rio area codes start with 2)
missing_ddi_re = re.compile(r'^\D*2\d\D*(\d\D?)?\d{4}\D?\d{4}$')
# missing +55 2X
missing_ddd_re = re.compile(r'^(\d\D?)?\d{4}\D?\d{4}$')


def update_phone(p):
    if phone_ok_re.search(p) or phone_0800_ok_re.search(p):
        pass
    elif wrong_separators_re.search(p):
        p = re.sub('\D', '', p)
        p = '+' + p[:2] + ' ' + p[2:4] + ' ' + p[4:]
    elif wrong_separators_0800_re.search(p):
        p = re.sub('\D', '', p)
        p = re.sub('^(55)?\d{2}?0800', '0800', p)
        p = p[:4] + ' ' + p[4:7] + ' ' + p[7:]
    elif missing_ddi_re.search(p):
        p = re.sub('\D', '', p)
        p = '+55 ' + p[:2] + ' ' + p[2:]
    elif missing_ddd_re.search(p):
        # not much we can do about it
        # later we could cross check the area code with the one correspondent to address.city
        p = re.sub('\D', '', p)

    return p


def audit_phone(phone_formats, problem_phones, phone):
    # splits multiple phones
    phones = re.split(';|,', phone)
    for p in phones:
        # dropping empty strings
        if len(p) == 0:
            continue

        p = update_phone(p)

        if phone_ok_re.search(p) or phone_0800_ok_re.search(p):
            phone_formats['ok'] += 1
        elif wrong_separators_re.search(p) or wrong_separators_0800_re.search(p):
            phone_formats['wrong_separators'] += 1
        elif missing_ddi_re.search(p) or missing_ddd_re.search(p):
            phone_formats['missing_area_code'] += 1
        else:
            phone_formats['other'] += 1
            problem_phones.append(p)

    return (phone_formats, problem_phones)


def is_phone(tag):
    return (tag.attrib['k'] == "phone")


def audit(osmfile):
    osm_file = open(osmfile, "rb")
    phone_formats = {
        'ok': 0,
        'wrong_separators': 0,
        'missing_area_code': 0,
        'other': 0}
    problem_phones = list()
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_phone(tag):
                    audit_phone(phone_formats, problem_phones, tag.attrib['v'])
    osm_file.close()
    return (phone_formats, problem_phones)


def print_phones():
    phone_formats, problem_phones = audit(INPUT_PATH)

    try: 
        os.makedirs(OUTPUT_DIR)
    except OSError:
        if not os.path.isdir(OUTPUT_DIR):
            raise

    with open(OUTPUT_PATH_FORMATS, 'wb') as output:
        output.write(json.dumps(phone_formats, indent=2))

    with open(OUTPUT_PATH_PROBLEM, 'wb') as output:
        output.write(json.dumps(problem_phones, indent=2))

    pprint.pprint(phone_formats)
    return phone_formats


if __name__ == '__main__':
    print_phones()