# <!><!> Programa que carga y limpia los datos del censo

import pandas as pd
import geopandas as gpd
import unidecode

def census_clean_ind(data):
    '''
    Limpieza de datos individuales para el censo
    '''
    data = str(data)
    data = data.replace('*', 'nan')
    data = data.replace('N/D', 'nan')
    data = float(data)
    return data


def census_clean(data):
    '''
    Función para impiar datos del censo
    '''
    data = data.apply(lambda x: str(x).replace('*', 'nan'))
    data = data.apply(lambda x: str(x).replace('N/D', 'nan'))
    data = data.apply(float)
    return data


def mun_clean(data):
    '''
    Función que ayuda a la limpieza de
    datos de nombres de municipio
    '''
    data = data.lower()
    data = unidecode.unidecode(data)
    data = data.replace('.', '')
    return data


def ageb_finder(data, data_agebs):
    '''
    Geolocalización de puntos a nivel ageb
    '''
    mun_dd = data['mun_id']
    point_dd = data['geometry']
    ageb_to_find_df = data_agebs[data_agebs['CVEGEO'].apply(lambda x: x[0:5])== mun_dd].copy()
    ageb_candidates = ageb_to_find_df[ageb_to_find_df['geometry'].apply(lambda x:
                                                                        point_dd.within(x))]
    if len(ageb_candidates) > 0:
        cvegeo_dd = ageb_candidates.iloc[0]['CVEGEO']
    else:
        cvegeo_dd = 'NaN'
    return cvegeo_dd


def geo_raw_load(root, ageb_folder, path_ageb, init_proj, end_proj):

    '''
    Carga de datos geográficos a nivel AGEB.
    La ubicación es en ageb_folder + path_ageb.

    init_proj es la proyección original de polígonos en CRS
    end_proj es la proyección final
    '''

    census_2020_geo = gpd.read_file(root + ageb_folder + path_ageb,
                                    geom='geometry', crs=init_proj)

    census_2020_geo = census_2020_geo.to_crs(end_proj)

    return census_2020_geo


def load_and_clean_census(root, path_data, census_2020_agebs):
    '''
    Carga datos del censo, los limpia y crea las claves homologadas
    '''

    # Creacion de claves homologadas de AGEB

    census_2020_data = pd.read_csv(root + path_data)
    census_2020_data = \
        census_2020_data[census_2020_data['NOM_LOC'].str.contains('Total AGEB')].copy()
    census_2020_data['ENTIDAD'] = census_2020_data['ENTIDAD'].apply(lambda x: f'{x:02d}')
    census_2020_data['MUN'] = census_2020_data['MUN'].apply(lambda x: f'{x:03d}')
    census_2020_data['LOC'] = census_2020_data['LOC'].apply(lambda x: f'{x:04d}')
    census_2020_data['CVEGEO'] = \
        census_2020_data['ENTIDAD'] + census_2020_data['MUN'] + \
        census_2020_data['LOC'] + census_2020_data['AGEB']
    census_2020 = census_2020_data.join(census_2020_agebs.set_index('CVEGEO'), on='CVEGEO').copy()

    #Final cleaning to dump
    census_2020.iloc[:,8:-6] = census_2020.iloc[:,8:-6].applymap(census_clean_ind).copy()
    census_2020.iloc[:, 1:8] = census_2020.iloc[:, 1:8].applymap(str).copy()
    census_2020_f = census_2020.iloc[:, 1:-5].copy()

    # Select geometries

    geometries_ageb = census_2020[['CVEGEO', 'geometry']].copy()
    geometries_ageb = geometries_ageb.dropna().copy()

    return census_2020_f, geometries_ageb


def dict_generation_mun(census_2020_mun):
    '''
    Genera diccionario de municipios para hacer más rápida
    la georreferencia en scripts futuros
    '''
    census_2020_mun['NOMGEO'] = census_2020_mun['NOMGEO'].apply(mun_clean)
    mun_to_dict = census_2020_mun[['NOMGEO', 'CVEGEO']].copy()
    return mun_to_dict

def cleaning_census():
    '''
    Función general que limpia el censo a nivel ageb, homogeiniza claves,
    limpia las geometrías y genera los diccionarios de municipios
    '''
    # Datos Censo
    str_state = '09'
    state_name = 'ciudaddemexico'
    root = ''
    ageb_folder = '/Users/carloscalderon/Downloads/AGEB_Manzanas_censo_2020/'
    state_root = str_state + '_' + state_name
    path_ageb = state_root + '/conjunto_de_datos/' + str_state + 'a.shp'
    path_mun = state_root + '/conjunto_de_datos/' + str_state + 'mun.shp'
    path_data = 'RESAGEBURB_09CSV20.csv'
    init_proj = "EPSG:3395"
    end_proj = "EPSG:4326"

    # Importamos AGEB
    census_2020_agebs = geo_raw_load(root, ageb_folder, path_ageb, init_proj, end_proj)

    # Importamos municipios

    census_2020_mun = geo_raw_load(root, ageb_folder, path_mun, init_proj, end_proj)

    #Limpieza Censo
    # Creacion de claves homologadas de AGEB

    census_2020_f, geometries_ageb = load_and_clean_census(root, path_data, census_2020_agebs)
    census_2020_f.to_csv(root + '/data' + 'data_agebs_2020.csv', index = False)
    geometries_ageb.to_csv(root + '/data' + 'geometries_agebs_2020.csv', index = False)


    # Dict Municipios

    mun_to_dict = dict_generation_mun(census_2020_mun)
    mun_to_dict.to_csv(root + '/data' +  'dict_municipios_CDMX.csv', index = False)


def main():
    cleaning_census()


if __name__ == "__main__":
    main()
