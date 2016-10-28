import re

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
    """Updates phones according to the regex classification"""
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


def handle_phone(phone):
    """Returns the updated phones list"""
    # splits multiple phones
    phones = re.split(';|,', phone)
    updated_phones = list()
    for p in phones:
        # dropping empty strings
        if len(p) == 0:
            continue
        p = update_phone(p)
        updated_phones.append(p)
    return updated_phones