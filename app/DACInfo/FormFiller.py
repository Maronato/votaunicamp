# coding: utf-8
import requests
from bs4 import BeautifulSoup
import re


def captcha_solver(html):
    numeros = {
        'um': 1,
        'dois': 2,
        'quatro': 4,
        'cinco': 5,
        'seis': 6,
        'sete': 7,
        'oito': 8,
        'nove': 9,
        'dez': 10,
    }
    try:
        captcha = BeautifulSoup(html, 'html.parser')
        captcha = captcha.find(id='campo_captcha')
        texto = re.findall(r'\\xe9 (.*?)\?', str(captcha.contents))
        r = 0
        f = 2
        for key, value in numeros.iteritems():
            ns = re.findall(key, texto[0])
            for _ in ns:
                r += value
                f -= 1
    except:
        return 0
    r += f*3
    return r


def get_pdf(key_code):
    if not key_code:
        return 1

    link = 'https://www.daconline.unicamp.br/ActionConsultaDiploma.asp'
    session = requests.Session()
    resp = session.get(link)
    captcha = captcha_solver(resp.content)
    if captcha is 0:
        return captcha
    header = {
        'Referer': 'https://www.daconline.unicamp.br/ActionConsultaDiploma.asp'
    }
    form_data = {
        'NOME_ELEMENTO_PROXY_HTML_ACTION': '/pckAcadConsultas/Diploma/BndDiploma.jsp',
        'tipo_consulta': 2,
        'rg': '',
        'data_nascimento': '',
        'tipo_documento': 1,
        'data_colacao': '',
        'tipo_documento_chave': 4,
        'codigo_chave': key_code,
        'val_antispam': captcha,
        'cmdAvancar': 'Aguarde...'
    }
    try:
        cookies = requests.utils.cookiejar_from_dict(requests.utils.dict_from_cookiejar(session.cookies))
        resp = session.post(link, data=form_data, headers=header, cookies=cookies)
    except:
        return 0
    return resp.content
