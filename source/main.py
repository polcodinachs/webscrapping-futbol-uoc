# coding=utf-8


### Càrrega de les llibreries a utilitzar
from sys import argv
import requests
import pandas as pd
import argparse
from bs4 import BeautifulSoup


### Headers utilitzats per al web scrapping
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}


"""Es realitza el primer request mitjançant BeautifulSoup per tal d'extreure un llistat de tots els enfrontaments que hi ha hagut en la temporada seleccionada. 
Es realitzen 38 iteracions (ja que les temporades espanyoles contenen 38 jornades) a la següent url:
www.resultados-futbol.com/primera/{any}/grupo1/jornada{n}
On {any} és la temporada especificada en la comanda i {n} és cadascuna de les jornades 1..38.
En aquestes iteracions, s'accedeix a les files d'una taula amb classe "vevent" que és d'on s'extreurà els noms dels equips locals i equips visitants que s'enfronten en aquella jornada."""

def partits (year):
    matchlist = []
    for i in range(1,39):
        url = ("https://www.resultados-futbol.com/primera" + str(year) + "/grupo1/jornada" + str(i))
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, features="html.parser")
        for item in soup.find_all('tr', class_="vevent"):
            for match in item.find_all('a', class_="url", href=True):
                if str(match['href'][9:][-5:]) == ("/" + str(year)):
                    matchlist.append(str(match['href'][9:][:-5]))
                else:
                    matchlist.append(str(match['href'][9:]))
    return [matchlist, year]

"""S'utilitza aquesta llista de sortida, que conté un llistat amb tots els partits i l'any de joc, en una altra funció que realitzarà iteracions 
sobre cada enfrontament de la llista i utilitzar-lo en la següent url:
www.resultados-futbol.com/partido/{equip local}/{equip visitant}/{any}
S'accedeix a una taula continguda a cada pàgina i s'accedeixen a les diferents columnes (td) de les files (tr) amb classe "barstyle bar4". 
Amb l'informació extreta es genera una llista per a les dades de l'equip local i una llista per a les dades de l'equip visitant que s'acaben concatenant.
Finalment, mitjançant la llibreria pandas, es genera el dataset de sortida amb les respectives columnes."""

def dataset (partits):
    llista_partits = partits[0]
    any = partits[1]
    local_visitant = []
    df = []
    n = 1
    n_partit = 0
    print("Jornada " + str(n))
    for i in llista_partits:
        local = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        visitant = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        if (any == 2023):
            url = ("https://www.resultados-futbol.com/partido/" + str(i))
        else:
            url = ("https://www.resultados-futbol.com/partido/" + str(i) + "/" + str(any))
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, features="html.parser")
        parameters = ['Posesión del balón', 'Goles', 'Tiros a puerta', 'Tiros fuera', 'Total tiros', 'Paradas del portero', 'Saques de esquina', 'Fueras de juego', 'Tarjetas Amarillas', 'Tarjetas Rojas', 'Asistencias', 'Tiros al palo', 'Lesiones', 'Sustituciones', 'Faltas', 'Penalti cometido']
        for index, table in enumerate(soup.find_all('tr', class_="barstyle bar4")):
            local[parameters.index(table.find_all('td')[1].text)] = table.find_all('td')[0].text
            visitant[parameters.index(table.find_all('td')[1].text)] = table.find_all('td')[2].text
        n_partit = n_partit + 1    
        local_visitant = local + visitant
        print("=" * n_partit)
        local_visitant.insert(0, str(int(any)-1) + "/" + str(any))
        local_visitant.insert(1, n)
        local_visitant.insert(2, i)
        local_visitant.insert(3, str(i).split('/')[0])
        local_visitant.insert(4, str(i).split('/')[1])
        df.append(local_visitant)
        if n_partit == 10:
            n = n + 1
            n_partit = 0
            print("Jornada " + str(n))
    df = pd.DataFrame(df)
    column_names = ['Temporada', 'Jornada', 'Partit', 'L', 'V', 'L-P', 'L-G', 'L-XP', 'L-XF', 'L-XT', 'L-PP', 'L-C', 'L-FJ', 'L-TG', 'L-TV', 'L-AS', 'L-XPA', 'L-L', 'L-S', 'L-F', 'L-PC', 'V-P', 'V-G', 'V-XP', 'V-XF', 'V-XT', 'V-PP', 'V-C', 'V-FJ', 'V-TG', 'V-TV', 'V-AS', 'V-XPA', 'V-L', 'V-S', 'V-F', 'V-PC']
    df.columns = column_names
    df.to_csv('dataset.csv')
    print(df)

year = argv[1]
dataset(partits(year))
