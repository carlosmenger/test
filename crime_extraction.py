# <!><!> Descarga de datos de crímenes a través de la API de la CDMX

import ssl
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_data(URL,
            root):
    '''
    Descarga los datos de incidencia delictiva
    de la página de datos abiertos de la CDMX
    a través de la API. Seguir URL para más
    info
    '''
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")

    urls = []
    for a_href in soup.find_all("a", href=True):
        urls.append(a_href["href"])

    urls = [k for k in urls if '.csv' in k]
    url = urls[0]
    ssl._create_default_https_context = ssl._create_unverified_context
    dataframe = pd.read_csv(url)
    dataframe.to_csv(root + '/data/' + 'carpetas.csv', index=False)

    return dataframe



def limpiar_delitos(dataframe, root, categories_scrapp, incidents_scrapp):
    '''
    Limpia y filtra los datos de la fiscalía
    '''

    dataframe = dataframe[['fecha_hechos',
             'delito',
             'categoria_delito',
             'alcaldia_hechos',
             'latitud',
             'longitud']].copy()

    dataframe2 = dataframe[dataframe['categoria_delito'].str.contains(categories_scrapp, regex=True)|
             dataframe['delito'].str.contains(incidents_scrapp, regex=True)].copy()

    dataframe2["latitud"] = pd.to_numeric(dataframe2["latitud"])
    dataframe2["longitud"] = pd.to_numeric(dataframe2["longitud"])
    dataframe2["fecha_hechos"] = pd.to_datetime(dataframe2["fecha_hechos"])

    dataframe2 = dataframe2[dataframe2.fecha_hechos.notnull() &
              dataframe2.latitud.notnull() &
              dataframe2.longitud.notnull() &
              dataframe2.delito.notnull()]

    dataframe2.to_csv(root + '/data/' + 'carpetas_limpio.csv', index=False)


def get_and_clean_data(URL,
                        root,
                        categories_scrapp,
                        incidents_scrapp):

    '''
    Descarga datos y luego los limpia
    dados los valores dados
    en url, categories_scrapp,
    '''
    dataframe = get_data(URL,
                  root)
    limpiar_delitos(dataframe, root, categories_scrapp, incidents_scrapp)


def main():
    '''
    Descarga los datos y los limpia según los valores
    default definidos en root, URL, categories_scrapp y
    incidents_scrapp
    '''
    root = ''
    URL = "https://datos.cdmx.gob.mx/dataset/carpetas-de-investigacion-fgj-de-la-ciudad-de-mexico/resource/48fcb848-220c-4af0-839b-4fd8ac812c0f"
    categories_scrapp = '(HOMICIDIO DOLOSO|SECUESTRO|LESIONES DOLOSAS|LESIONES INTENCIONALES|ROBO DE VEHÍCULO)'
    incidents_scrapp = '(LESIONES DOLOSAS|LESIONES INTENCIONALES|ROBO A TRANSEUNTE|ROBO A NEGOCIO|ROBO DE AUTO|ROBO DE VEHÍCULO|ROBO A CASA)'
    get_and_clean_data(URL,
                        root,
                        categories_scrapp,
                        incidents_scrapp)

if __name__ == "__main__":
    main()
