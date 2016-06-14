# -*- coding: utf-8 -*-
from .FormFiller import get_pdf
from .PdfHandler import convert_pdf, get_field
from .PdfDownloader import download_pdf


def check_code(key_code):
    pdf = get_pdf(key_code)
    if pdf is 1:
        return 0, "O código é necessário"
    elif pdf is 0:
        return 0, 'DAC falhou. Tente novamente.'

    name = download_pdf(pdf)
    if name is 0:
        return 0, 'Ocorreu um erro no servidor'

    text = convert_pdf(name)
    if text is 0:
        return 0, "Código inválido"
    return 1, text


def check_fields(text):
    fields = {
        'nome': get_field('Nome', text),
        'rg': get_field('Documento de Identidade', text),
        'curso': get_field('Dados do Ingresso', text),
        'situacao': get_field('Situação no Curso', text),
        'ra': get_field('Registro Acadêmico', text),
        'nivel': get_field('Nível', text),
    }
    return fields

