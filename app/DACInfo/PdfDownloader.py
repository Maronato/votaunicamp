# coding: utf-8
import random
import string


def random_name():
    name = str(''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10)))
    name += '.pdf'
    return name


def download_pdf(resp):
    name = random_name()
    try:
        pdf = open(name, 'w')
        pdf.write(resp)
        pdf.close()
    except:
        return 0
    return name
