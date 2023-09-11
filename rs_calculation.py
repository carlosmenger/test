# <!><!> Script que calcula el índice de riesgo dada la tasa de inciencia

import pandas as pd
import numpy as np

# Global variables

periods = ['rate_2016_log',
           'rate_2017_log',
           'rate_2018_log',
           'rate_2019_log',
           'rate_2020_log',
           'rate_2021_log',
           'rate_last_12_months_log',
           'rate_last_6_months_log',
           'rate_last_3_months_log',
           'rate_historic_log']

periods_dict = {'rate_2016_log': '2016',
                'rate_2017_log': '2017',
                'rate_2018_log': '2018',
                'rate_2019_log': '2019',
                'rate_2020_log': '2020',
                'rate_2021_log': '2021',
                'rate_last_12_months_log': 'last_12_months',
                'rate_last_6_months_log': 'last_6_months',
                'rate_last_3_months_log': 'last_3_months',
                'rate_historic_log': 'historic'}


vars_rs_individual = ['rs_101_2016',
                      'rs_101_2017',
                      'rs_101_2018',
                      'rs_101_2019',
                      'rs_101_2020',
                      'rs_101_2021',
                      'rs_101_last_3_months',
                      'rs_101_last_6_months',
                      'rs_101_last_12_months',
                      'rs_101_historic',
                      'rs_102_2016',
                      'rs_102_2017',
                      'rs_102_2018',
                      'rs_102_2019',
                      'rs_102_2020',
                      'rs_102_2021',
                      'rs_102_last_3_months',
                      'rs_102_last_6_months',
                      'rs_102_last_12_months',
                      'rs_102_historic',
                      'rs_103_2016',
                      'rs_103_2017',
                      'rs_103_2018',
                      'rs_103_2019',
                      'rs_103_2020',
                      'rs_103_2021',
                      'rs_103_last_3_months',
                      'rs_103_last_6_months',
                      'rs_103_last_12_months',
                      'rs_103_historic',
                      'rs_105_2016',
                      'rs_105_2017',
                      'rs_105_2018',
                      'rs_105_2019',
                      'rs_105_2020',
                      'rs_105_2021',
                      'rs_105_last_3_months',
                      'rs_105_last_6_months',
                      'rs_105_last_12_months',
                      'rs_105_historic',
                      'rs_300_2016',
                      'rs_300_2017',
                      'rs_300_2018',
                      'rs_300_2019',
                      'rs_300_2020',
                      'rs_300_2021',
                      'rs_300_last_3_months',
                      'rs_300_last_6_months',
                      'rs_300_last_12_months',
                      'rs_300_historic',
                      'rs_400_2016',
                      'rs_400_2017',
                      'rs_400_2018',
                      'rs_400_2019',
                      'rs_400_2020',
                      'rs_400_2021',
                      'rs_400_last_3_months',
                      'rs_400_last_6_months',
                      'rs_400_last_12_months',
                      'rs_400_historic',
                      'rs_500_2016',
                      'rs_500_2017',
                      'rs_500_2018',
                      'rs_500_2019',
                      'rs_500_2020',
                      'rs_500_2021',
                      'rs_500_last_3_months',
                      'rs_500_last_6_months',
                      'rs_500_last_12_months',
                      'rs_500_historic',
                       ]

vars_rs_combined = ['rs_all_2016', 'rs_all_2017', 'rs_all_2018',
                    'rs_all_2019', 'rs_all_2020', 'rs_all_2021',
                    'rs_all_last_12_months', 'rs_all_last_6_months',
                    'rs_all_last_3_months', 'rs_all_historic',
                    'actual_risk']


# inicia script RS


def ecdf_function(xdata):
    '''
    Genera la ECDF (Empirical Density Cumulative Function)
    dado un conjunto de datos
    '''
    xdataecdf = np.sort(xdata)
    ydataecdf = np.arange(1, len(xdata) + 1) / len(xdata)
    return xdataecdf, ydataecdf


def cutter(data_x, data_y, treshold):
    '''
    Crea un corte sobre la ECDF
    dado el valor de treshold
    '''
    data_x = np.sort(data_x)
    data_y = np.sort(data_y)
    select_data_below = data_y[data_y < treshold]
    cutter_y = len(select_data_below)
    cutter_x = data_x[cutter_y]
    return cutter_x


def risk_score(value, tresholds):
    '''
    La evalación de riesgo está asociado a si se encuentra
    arriba oabajo de cierto quantil definido en
    treshold
    '''
    risk_score = len(tresholds)
    for i, limit in enumerate(tresholds):
        if value <= limit:
            risk_score = i
            break
    return risk_score


def parameter_calculation(data_rates, periods_dict):
    '''
    Dadas las tasas de incidencia y los periodos de
    análisis, genera los parametros para la evaluación de
    riesgo
    '''
    periods = list(periods_dict.keys())
    crimes = list(data_rates['incident_type'].unique())
    parameters = []

    for crime in crimes:
        for period in periods:
            d_robos = data_rates[data_rates['incident_type']==crime].copy()
            data_robos_values = d_robos[(d_robos[period]>-1e10)&(d_robos[period]<1e10)][period]
            sample = data_robos_values.values
            rates, cumulative_probability = ecdf_function(sample)
            cuts = []
            if len(cumulative_probability) > 10:
                valid = True
                for i in np.arange(0, 1.0, 0.2):
                    cut = cutter(rates, cumulative_probability, i)
                    cuts.append(cut)
            else:
                valid = False
                cuts = [0, 0, 0, 0, 0]
            parameters.append([period, crime, cuts, valid])

    parameters_df = pd.DataFrame(parameters, columns=['metric',
                                                      'incident_type',
                                                      'cuts',
                                                      'is_valid'])
    parameters_df['period'] = parameters_df['metric'].apply(lambda x: periods_dict.get(x, 'nan'))

    return parameters_df


def rs_individual(data_rates, parameters_df, periods_dict):
    '''
    Calcula el indice de riesgo basándose en las tasas de
    incidencia, los parámetros (cortes) y los periodos
    en donde se calcula la incidencia
    '''

    periods = list(periods_dict.keys())
    risk_score_df = pd.DataFrame()
    risk_score_df['ageb_id'] = data_rates['ageb_id'].unique()
    risk_score_df = risk_score_df.set_index('ageb_id')

    incidents_types = list(parameters_df['incident_type'].unique())
    periods = list(parameters_df['period'].unique())

    for incident_type in incidents_types:

        dd = data_rates[(data_rates['incident_type']==incident_type)].copy()
        dd = dd.set_index('ageb_id')

        for period in periods:

            metric = 'rate_' + period + '_log'
            parameters_to_use = parameters_df[(parameters_df['incident_type']==incident_type)&
                                              (parameters_df['period']==period)]

            cuts = parameters_to_use['cuts'].iloc[0]
            is_valid = parameters_to_use['is_valid'].iloc[0]
            name_column = 'rs_' + str(incident_type) + '_' + period

            if is_valid:
                results = dd[metric].apply(lambda x: risk_score(x, cuts))
                risk_score_df[name_column] = results

            else:
                results = dd[metric].apply(lambda x: float('nan'))
                risk_score_df[name_column] = results

    return risk_score_df


def rs_combined(risk_score_df, parameters_df, weights):
    '''
    Calcula el índice de riesgo combinado
    utilizando distintos tipos de incidentes
    '''

    periods = list(parameters_df['period'].unique())
    incident_types = list(parameters_df['incident_type'].unique())
    risk_score_df.replace(np.nan, 0,inplace=True)

    rs_dict = {}
    for period in periods:
        metrics = []
        for incident_type in incident_types:
            metric = 'rs' + '_' + str(incident_type) + '_' + period
            metrics.append(metric)
        rs_dict[period] = metrics

    sum_weights = sum(weights)

    for period in rs_dict.keys():
        test = risk_score_df[rs_dict[period]]
        risk_score_df['rs_all_' + period]  = ((test * weights).apply(sum, axis=1)) / sum_weights

    actual_risk = ['rs_all_last_3_months',
                   'rs_all_last_6_months',
                   'rs_all_last_12_months',
                   'rs_all_historic'
                  ]
    risk_score_df['actual_risk'] = risk_score_df[actual_risk].apply(sum, axis=1) / len(actual_risk)

    return risk_score_df


def rs_generator(root, rates_path):
    '''
    Unificación de todo el script
    Genera la tabla de parámetros, rs_by_crime y rs_df_combined
    '''
    rates = pd.read_csv(root + rates_path)
    weights = [5, 5, 10, 11, 49, 27, 4]

    parameters_df = parameter_calculation(rates, periods_dict)

    risk_score_df = rs_individual(rates, parameters_df, periods_dict)

    rs_by_crime = risk_score_df[vars_rs_individual].reset_index()
    rs_by_crime.replace([-np.inf, np.inf], np.nan,inplace=True)

    rs_df_combined = rs_combined(risk_score_df, parameters_df, weights)
    rs_df_combined = rs_df_combined[vars_rs_combined].reset_index()
    rs_df_combined.replace([-np.inf, np.inf], np.nan,inplace=True)
    vars_raw = list(rs_df_combined.iloc[:, 1:].columns)
    vars_float = list(map(lambda x: x + '_float', vars_raw))
    rs_df_combined[vars_float] = rs_df_combined[vars_raw]
    rs_df_combined[vars_raw] = rs_df_combined[vars_raw].applymap(round)

    return parameters_df, rs_by_crime, rs_df_combined


def export_data_rs(root, parameters_df, rs_by_crime, rs_df_combined):
    '''
    Exporta los datos generados por este script en .csv
    '''

    parameters_df.to_csv(root + '/data/' + 'rs_parameters.csv', index = False)
    rs_by_crime.to_csv(root + '/data/' + ' rs_by_crime.csv', index=False)
    rs_df_combined.to_csv(root + '/data/' + 'rs_df_combined.csv', index=False)


def main():
    '''
    Calcula el índice de riesgo dado
    el archivo de tasas de incidencia
    '''
    root = '/data/'
    rates_path = 'incident_rates.csv'
    parameters_df, rs_by_crime, rs_df_combined = rs_generator(root, rates_path)
    export_data_rs(root, parameters_df, rs_by_crime, rs_df_combined)

if __name__ == "__main__":
    main()
