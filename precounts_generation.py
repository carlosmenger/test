# <!><!> Cálculo de agregados mensuales y tasas a nivel AGEB

import pandas as pd
import geopandas as gpd
import numpy as np
from shapely import wkt


# Variables globales

root = ''

census_path = 'data_agebs_2020.csv'

incidents_path = 'tecnotrust_incidents.csv'

special_rates = ['rate_last_12_months',
                 'rate_last_6_months',
                 'rate_last_3_months',
                 'rate_historic']

dict_categorias_id = {'robo a persona': '101',
                      'robo a negocio': '102',
                      'robo a casa': '103',
                      'robo de auto': '105',
                      'homicidio': '300',
                      'secuestro': '400',
                      'lesiones': '500',
                     }

incidents_type = ['robo a persona',
                  'robo a negocio',
                  'robo a casa',
                  'robo de auto',
                  'homicidio',
                  'secuestro',
                  'lesiones']

incidents_code = ['101', '102', '103', '105', '300', '400', '500']

weights = [5, 5, 10, 11, 49, 27, 4]

multiplier = 100000

# INICIA PRE COUNTS

def label_counts_generator(dates_name):
    '''
    Genera las etiquetas para la tabla de precounts
    '''

    labels_counts = ['ageb_id',
                     'incident_type']
    for date in dates_name:
        labels_counts.append(date)
    return labels_counts


def label_rate_generator(years, special_rates):
    '''
    General las etiquetas para la tabla de rates
    '''
    labels_rates = ['ageb_id',
                    'incident_type']
    for year in years:
        labels_rates.append('rate_' + year)

    labels_rates += special_rates

    for year in years:
        labels_rates.append('rate_' + year + '_log')

    special_rates_log = list(map(lambda x: x + '_log', special_rates))

    for special_rate_log in special_rates_log:
        labels_rates.append(special_rate_log)

    return labels_rates


def incident_types_generator(root):
    '''
    Genera los incident types con su peso
    '''
    info_incidents = pd.DataFrame(columns=['incidents_type',
                                           'incidents_code',
                                           'weights'])
    info_incidents['incidents_type'] = incidents_type
    info_incidents['incidents_code'] = incidents_code
    info_incidents['weights'] = weights
    return info_incidents


def geo_load(root, path, proj):
    '''
    Carga datos geográficos con la proyección correcta
    '''
    geo_df = pd.read_csv(root+path)
    geo_df['geometry'] = geo_df['geometry'].apply(lambda x: wkt.loads(x))
    correct_geo_df = gpd.GeoDataFrame(geo_df, geometry='geometry', crs=proj)
    return correct_geo_df


def precounts_generator(data_precounts):
    '''
    Genera conteos mensuales, anuales
    y por periodos a nivel ageb
    '''

    dates = data_precounts['month'].sort_values().unique()
    incident_types = data_precounts['incident_type'].unique()
    all_agebs = data_precounts['cvegeo_ageb'].unique()
    data_geo_group = data_precounts.groupby('cvegeo_ageb')

    results_dates = []
    for ageb_id in all_agebs:
        del_ageb = data_geo_group.get_group(ageb_id)
        for incident_type in incident_types:
            list_ids = [ageb_id, incident_type]
            filter_incidents = del_ageb[del_ageb['incident_type']==incident_type]
            if len(filter_incidents) > 0:
                list_values = []
                for i in range(len(dates)):
                    first_date = dates[i-1]
                    last_date = dates[i]
                    filter_dates = filter_incidents[(filter_incidents['fecha_hechos'] > first_date) &
                                                    (filter_incidents['fecha_hechos'] <= last_date)].copy()
                    if len(filter_dates) > 0:
                        count_incidents = len(filter_dates)
                    else:
                        count_incidents = 0
                    list_values.append(count_incidents)
                results_dates.append(list_ids + list_values)
            else:
                list_values = list(np.zeros(len(dates)-1))
                results_dates.append(list_ids + list_values)

#   Evaluación de tasas

    dates_name = list(map(lambda x: str(x)[0:7], dates))
    #dates_name = dates_name[:-1]
    years = list(set(map(lambda x: str(x)[0:4], dates)))
    dict_day_normalizer = {}
    column_name = ['ageb_id', 'incident_type'] + dates_name
    pre_counts = pd.DataFrame(results_dates, columns=column_name)

    for year in years:
        year_months = list(map(lambda x: x.find(year), dates_name))
        positions = [i for i, e in enumerate(year_months) if e == 0]
        names_year_month = [dates_name[i] for i in positions]
        pre_counts[year] = pre_counts[names_year_month].apply(sum, axis=1)
        date_times_year_month = pd.to_datetime(names_year_month)
        days = (max(date_times_year_month) - min(date_times_year_month)).days + 31
        dict_day_normalizer[year] = days


    names_last_12_months = dates_name[-13:-1]
    names_last_6_months = dates_name[-7:-1]
    names_last_3_months = dates_name[-4:-1]

    pre_counts['last_12_months'] = pre_counts[names_last_12_months].apply(sum, axis=1)
    pre_counts['last_6_months'] = pre_counts[names_last_6_months].apply(sum, axis=1)
    pre_counts['last_3_months'] = pre_counts[names_last_3_months].apply(sum, axis=1)
    pre_counts['historic'] = pre_counts[dates_name[:-1]].apply(sum, axis=1)

    return pre_counts, dict_day_normalizer, dates_name, years


def rate_generator(data_precounts, data_census, dict_day_normalizer, dates_name, years):
    '''
    Genera tasas de incidencia a nivel ageb a nivel anual y por periodo
    '''

    final_data = data_precounts.join(data_census.set_index('CVEGEO'), on='ageb_id')

    for year in years:
        normalizer = final_data['POBTOT'] * dict_day_normalizer[year]
        final_data['rate_' + year] = multiplier * final_data[year] / (normalizer)
        final_data['rate_' + year + '_log'] = final_data['rate_' + year].apply(np.log)

    normalizer_days = 365 * final_data['POBTOT']

    final_data['rate_last_12_months'] = multiplier * final_data['last_12_months'] / (normalizer_days)
    final_data['rate_last_6_months'] = multiplier * final_data['last_6_months'] / (normalizer_days / 2)
    final_data['rate_last_3_months'] = multiplier * final_data['last_3_months'] / (normalizer_days / 4)

    final_data['rate_last_12_months_log'] = final_data['rate_last_12_months'].apply(np.log)
    final_data['rate_last_6_months_log'] = final_data['rate_last_6_months'].apply(np.log)
    final_data['rate_last_3_months_log'] = final_data['rate_last_3_months'].apply(np.log)

    tot_normalizer = final_data['POBTOT'] * sum(dict_day_normalizer.values())
    final_data['rate_historic'] = multiplier * (final_data['historic'] / tot_normalizer)
    final_data['rate_historic_log'] = final_data['rate_historic'].apply(np.log)

    labels_rates = label_rate_generator(years, special_rates)
    labels_precounts = label_counts_generator(dates_name)

    data_precounts = final_data[labels_precounts].copy()
    data_rates = final_data[labels_rates].copy()
    data_rates.replace(-np.inf, np.nan,inplace=True)

    return data_rates


def precounts(root, census_path, incidents_path):
    '''
    Función que genera los tres conjuntos
    principales de datos del script de
    precounts: incident_tpyes, pre_counts y rates
    '''

    # Importamos data del censo

    census_2020 = pd.read_csv(root + census_path)

    # Importamos datos georreferenciados

    data_del_geo = geo_load(root, incidents_path, 'EPSG:4326')

    # Generamos incident types

    incidents_types = incident_types_generator(root)

    #Asociación crímenes AGEB por mes (Precounts)

    pre_counts, dict_day_normalizer,  dates_name, years= precounts_generator(data_del_geo)

    # generación de tasas

    rates = rate_generator(pre_counts, census_2020, dict_day_normalizer, dates_name, years)

    return incidents_types, pre_counts, rates

def export_data_precounts(root, info_incidents, pre_counts, rates):

    info_incidents.to_csv(root + 'incident_types.csv', index = False)
    pre_counts.to_csv(root + 'precounts.csv', index=False)
    rates.to_csv(root + 'incident_rates.csv', index=False)


def main():
    incident_types, pre_counts, rates = precounts(root, census_path, incidents_path)
    export_data_precounts(root, incident_types, pre_counts, rates)


if __name__ == "__main__":
    main()
