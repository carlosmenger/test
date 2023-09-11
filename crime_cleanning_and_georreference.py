import pandas as pd
import geopandas as gpd
from shapely import wkt
import unidecode


dict_categorias = {'ROBO A TRANSEUNTE EN VIA PUBLICA CON VIOLENCIA': 'robo a persona',
                   'LESIONES INTENCIONALES': 'lesiones',
                   'LESIONES INTENCIONALES POR ARMA DE FUEGO': 'lesiones',
                   'ROBO A NEGOCIO SIN VIOLENCIA': 'robo a negocio',
                   'ROBO A TRANSEUNTE DE CELULAR CON VIOLENCIA': 'robo a persona',
                   'ROBO A CASA HABITACION SIN VIOLENCIA': 'robo a casa',
                   'ROBO A NEGOCIO CON VIOLENCIA': 'robo a negocio',
                   'LESIONES INTENCIONALES POR ARMA BLANCA': 'lesiones',
                   'ROBO A CASA HABITACION Y VEHICULO SIN VIOLENCIA': 'robo a casa',
                   'ROBO A TRANSEUNTE DE CELULAR SIN VIOLENCIA': 'robo a persona',
                   'ROBO A TRANSEUNTE EN VIA PUBLICA SIN VIOLENCIA': 'robo a persona',
                   'ROBO A TRANSEUNTE SALIENDO DEL BANCO CON VIOLENCIA': 'robo a persona',
                   'ROBO A CASA HABITACION CON VIOLENCIA': 'robo a casa',
                   'HOMICIDIO POR ARMA DE FUEGO': 'homicidio',
                   'LESIONES INTENCIONALES POR GOLPES': 'lesiones',
                   'HOMICIDIO POR AHORCAMIENTO': 'homicidio',
                   'ROBO A TRANSEUNTE EN NEGOCIO CON VIOLENCIA': 'robo a persona',
                   'ROBO A TRANSEUNTE EN PARQUES Y MERCADOS CON VIOLENCIA': 'robo a persona',
                   'HOMICIDIOS INTENCIONALES (OTROS)': 'homicidio',
                   'ROBO A TRANSEUNTE SALIENDO DEL CAJERO CON VIOLENCIA': 'robo a persona',
                   'HOMICIDIO POR ARMA BLANCA': 'homicidio',
                   'PLAGIO O SECUESTRO': 'secuestro',
                   'ROBO A TRANSEUNTE EN RESTAURANT CON VIOLENCIA': 'robo a persona',
                   'FEMINICIDIO': 'homicidio',
                   'ROBO A NEGOCIO Y VEHICULO SIN VIOLENCIA': 'robo a negocio',
                   'ROBO A CASA HABITACION Y VEHICULO CON VIOLENCIA': 'robo a casa',
                   'HOMICIDIO POR GOLPES': 'homicidio',
                   'ROBO A NEGOCIO Y VEHICULO CON VIOLENCIA': 'robo a negocio',
                   'ROBO A TRANSEUNTE Y VEHICULO CON VIOLENCIA': 'robo de auto',
                   'ROBO A TRANSEUNTE EN HOTEL CON VIOLENCIA': 'robo a persona',
                   'ROBO A TRANSEUNTE EN TERMINAL DE PASAJEROS CON VIOLENCIA': 'robo a persona',
                   'ROBO A TRANSEUNTE EN VIA PUBLICA (NOMINA) CON VIOLENCIA': 'robo a persona',
                   'ROBO A TRANSEUNTE EN CINE CON VIOLENCIA': 'robo a persona',
                   'ROBO A TRANSEUNTE CONDUCTOR DE TAXI PUBLICO Y PRIVADO CON VIOLENCIA': 'robo a persona',
                   'ROBO A TRANSEUNTE A BORDO DE TAXI PÚBLICO Y PRIVADO CON VIOLENCIA': 'robo a persona',
                   'FEMINICIDIO POR GOLPES': 'homicidio',
                   'ROBO A TRANSEUNTE A BORDO DE TAXI PUBLICO Y PRIVADO SIN VIOLENCIA': 'robo a persona',
                   'LESIONES INTENCIONALES Y ROBO DE VEHICULO': 'lesiones',
                   'FEMINICIDIO POR DISPARO DE ARMA DE FUEGO': 'homicidio',
                   'FEMINICIDIO POR ARMA BLANCA': 'homicidio',
                   'HOMICIDIO POR INMERSION': 'homicidio',
                   'ROBO A NEGOCIO SIN VIOLENCIA POR FARDEROS (TIENDAS DE AUTOSERVICIO)': 'robo a negocio',
                   'ROBO A NEGOCIO SIN VIOLENCIA POR FARDEROS (TIENDAS DE CONVENIENCIA)': 'robo a negocio',
                   'ROBO A NEGOCIO CON VIOLENCIA POR FARDEROS (TIENDAS DE CONVENIENCIA)': 'robo a negocio',
                   'ROBO A NEGOCIO CON VIOLENCIA POR FARDEROS (TIENDAS DE AUTOSERVICIO)': 'robo a negocio',
                   'LESIONES DOLOSAS POR QUEMADURAS': 'lesiones',
                   'SECUESTRO': 'secuestro',
                   'ROBO A TRANSEUNTE EN VIA PUBLICA (NOMINA) SIN VIOLENCIA': 'robo a persona',
                   'ROBO A NEGOCIO SIN VIOLENCIA POR FARDEROS': 'robo a negocio',
                   'ROBO DE VEHICULO DE SERVICIO PARTICULAR CON VIOLENCIA': 'robo de auto',
                   'ROBO DE VEHICULO DE SERVICIO PARTICULAR SIN VIOLENCIA': 'robo de auto',
                   'ROBO DE MOTOCICLETA SIN VIOLENCIA': 'robo de auto',
                   'ROBO DE MOTOCICLETA CON VIOLENCIA': 'robo de auto',
                   'ROBO DE VEHICULO DE SERVICIO DE TRANSPORTE SIN VIOLENCIA': 'robo de auto',
                   'ROBO DE VEHICULO DE SERVICIO DE TRANSPORTE CON VIOLENCIA': 'robo de auto',
                   'ROBO DE VEHICULO DE SERVICIO PÚBLICO SIN VIOLENCIA': 'robo de auto',
                   'ROBO DE VEHICULO DE SERVICIO OFICIAL SIN VIOLENCIA': 'robo de auto',
                   'ROBO DE VEHICULO DE SERVICIO OFICIAL CON VIOLENCIA': 'robo de auto',
                   'ROBO DE VEHICULO DE SERVICIO PÚBLICO CON VIOLENCIA': 'robo de auto',
                   'ROBO DE VEHICULO EN PENSION, TALLER Y AGENCIAS C/V': 'robo de auto',
                   'ROBO DE VEHICULO EN PENSION, TALLER Y AGENCIAS S/V': 'robo de auto',
                   'ROBO DE MAQUINARIA SIN VIOLENCIA': 'robo a persona',
                   'ROBO DE MAQUINARIA CON VIOLENCIA': 'robo a persona',
                  }

dict_categorias_id = {'robo a persona': '101',
                      'robo a negocio': '102',
                      'robo a casa': '103',
                      'robo de auto': '105',
                      'homicidio': '300',
                      'secuestro': '400',
                      'lesiones': '500',
                     }


def census_clean(data):
    '''
    Usamos esta función para impiar datos del censo
    '''
    data = data.apply(lambda x: str(x).replace('*', 'nan'))
    data = data.apply(lambda x: str(x).replace('N/D', 'nan'))
    data = data.apply(float)
    return data


def mun_clean(data):
    '''
    Limpieza de strings en municipios
    '''
    data = data.lower()
    data = unidecode.unidecode(data)
    data = data.replace('.', '')
    return data


def ageb_finder(data, data_agebs):
    '''
    Georreferencia de puntos a nivel AGEB
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


def ageb_load(root, path, proj):
    '''
    Carga de datos a nivel AGEB
    '''
    agebs_df = pd.read_csv(root + path)
    agebs_df['geometry'] = agebs_df['geometry'].apply(lambda x: wkt.loads(x))
    census_2020_agebs = gpd.GeoDataFrame(agebs_df, geometry='geometry', crs=proj)
    return census_2020_agebs


def dict_muni_load(root, path_muni_names):
    '''
    Carga de diccionario de municipios
    '''
    census_2020_mun_names = pd.read_csv(root+path_muni_names)
    census_2020_mun_names['NOMGEO'] = census_2020_mun_names['NOMGEO'].apply(mun_clean)
    census_2020_mun_names['CVEGEO'] = census_2020_mun_names['CVEGEO'].apply(lambda x: f'{x:05d}')
    dict_municipios = dict(census_2020_mun_names[['NOMGEO', 'CVEGEO']].values)
    return dict_municipios


def crime_load(root, incidents_path, proj):
    '''
    Carga de datos de crímenes
    '''
    data_delitos = gpd.read_file(root + incidents_path)
    data_delitos['geometry'] = gpd.points_from_xy(data_delitos['longitud'],
                                                  data_delitos['latitud'],
                                                  crs=proj)
    return data_delitos


def crime_clean(data_delitos, dict_municipios, dict_categorias):
    '''
    Limpieza de datos de crímenes
    '''

#   Asociamos municipio
    data_delitos['mun_id'] = \
        data_delitos['alcaldia_hechos'].apply(lambda x: dict_municipios.get(mun_clean(x), 'NaN'))
    data_del = data_delitos[data_delitos['mun_id'] != 'NaN'].copy()

#   Limpieza fechas
    data_del['fecha_hechos'] = pd.to_datetime(data_del['fecha_hechos'])
    data_del['day'] = data_del['fecha_hechos'].apply(lambda x: x.day)
    data_del['hour'] = data_del['fecha_hechos'].apply(lambda x: x.hour)
    data_del['month'] = \
        pd.to_datetime(data_del['fecha_hechos'].apply(lambda x:
                                                      str(x.year) + '-' + str(x.month)))
    data_del = data_del[data_del['month'] > '2015-12-31'].copy()

#   Categorización delitos

    data_del['incident_type_text'] = data_del['delito'].apply(lambda x: dict_categorias[x])
    data_del['incident_type'] = data_del['incident_type_text'].apply(lambda x:
                                                                     dict_categorias_id[x])

    return data_del

def crime_georef_ageb(data_del, census_2020_agebs):
    '''
    Georreferenia de crímenes a nivel ageb
    '''
    data_del['cvegeo_ageb'] = data_del.apply(lambda x: ageb_finder(x, census_2020_agebs), axis=1)
    data_del_geo = data_del[data_del['cvegeo_ageb'] != 'NaN'].copy()

    return data_del_geo


def export_crimes_georref(root, data_del_geo):
    '''
    Exportamos data
    '''
    data_del_geo.to_csv(root + '/data/' + 'tecnotrust_incidents.csv', index = False)


def georreference_and_cleaning(root, path_ageb,
                               path_muni_names,
                               path_incidents,
                               proj_ageb,
                               proj_delitos):
    '''
    Función que georreferencia los incidentes dados los puntos de la fiscalía
    y las geometrías del censo
    '''

    # Importamos agebs

    census_2020_agebs = ageb_load(root, path_ageb, proj_ageb)

    # Creamos diccionario municipios

    dict_municipios = dict_muni_load(root, path_muni_names)

    # Cargamos datos de crímenes

    data_delitos = crime_load(root, path_incidents, proj_delitos)

    # Limpiamos datos crímenes

    data_del = crime_clean(data_delitos, dict_municipios, dict_categorias)

    # Georreferenciamos datos de crímenes

    data_del_geo = crime_georef_ageb(data_del, census_2020_agebs)

    return data_del_geo


def main():
    '''
    Corremos la fnción georreference_and_cleaning
    con estos datos default y exportamos el resultado
    '''
    root = ''
    path_ageb = 'geometries_agebs_2020.csv'
    path_muni_names = 'dict_municipios_CDMX.csv'
    proj_ageb = "EPSG:4326"
    path_incidents = 'carpetas_limpio.csv'
    proj_delitos = "EPSG:4326"

    data_del_geo = georreference_and_cleaning(root, path_ageb, path_muni_names,
                                              path_incidents,
                                              proj_ageb,
                                              proj_delitos)

    export_crimes_georref(root, data_del_geo)

if __name__ == "__main__":
    main()
