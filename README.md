# Propuesta de evalación de riesgo criminal en CDMX


Conjunto de scripts en python que permiten generar data limpia y confiable
para medir el riesgo a  nivel AGEB en CDMX. Cada script genera .csv que 
posteriormente serán subidos a SQL

Installación previa

Crear un ambiente de python 3.8 o superior
Correr el archivo requirements.txt utilizando pip

Correr todos los scripts

Correr los scripts en el siguiente orden:

    1. cleanning_census.py
    2. crime_extraction.py
    3. crime_cleanning_and_georreference
    4. precounts_generation.py
    5. rs_calculation.py
    6. upload_rs_db.py

Descripción de scripts

Tenemos 6 scripts que engloban 4 procesos para la limpieza de datos. 
Cada uno de estos scripts cosume uno o varios csvs y exporta csvs. 
A continuaciñon describimos cada uno de estos scripts:

1-cleaning_census.py: 

Limpia los datos del censo para poder normalizar propiamente y tener geometrías 
a nivel AGEB válidas.
Inputs: 

    Data del censo


Outputs:

    'data_agebs_2020.csv': Data del censo 2020 del INEGI a nivel AGEB
    'geometries_agebs_2020.csv': Geometrías nivel AGEB del censo del 2020
    'dict_municipios_CDMX.csv': Lista de municipios de la CDMX

2-crime_extraction.py

Descarga los datos de la página del gobierno de la CDMX

Inputs: 

    NO NECESITA

Outputs: 

    'carpetas_limpio.csv': Data de los incidentes delictivos en la CDMX


3-crime_cleanning_and_georreference.py:

Limpia los datos de las carpetas de investigación de la CDMX. Filtra los que necesitamos
y finalmente los geolocaliza en una AGEB.

Inputs:

    'geometries_agebs_2020.csv'
    'dict_municipios_CDMX.csv'
    'carpetas_limpio.csv'


Outputs: 

    -tecnotrust_incidents.csv archivo de incidentes limpios y georreferenciados


4-precounts_generation.py

Agrupa los datos ya georreferenciados a nivel AGEB mensualmente. Esto ayuda a 
hacer cálculos más rápido. También calcula las tasas de incidencia delictiva.

Inputs:
    'data_agebs_2020.csv'
    'tecnotrust_incidents.csv'


Outputs:

    'incident_types.csv': Tipos de incidentes según la calificación propuesta
    'precounts.csv': Datos de incidencia delictiva agrupados a nivel de AGEB y
                    a nivel mensual y anual (desde 2017)
    'incident_rates.csv': Tasas de incidencia delictiva a nivel de AGEB y
                        a nivel mensual y anual (desde 2017)

5-rs_calculation.py

Calcula el nivel de riesgo paracada AGEB dados distintos periodos de tiempos. 
Este archivo genera los consumibles finales para la aplicación

Inputs:

    'incident_rates.csv'

Outputs:

    'rs_parameters.csv': Parámetros de evaluación de riesgo
    'rs_by_crime.csv': Calificación de riesgo por tipo de crimen a nivel AGEB
    'rs_df_combined.csv': Calificación de riesgo combinando 
                        distintos tipos de crímenes a nivel AGEB

6-upload_rs_db.py

Finalmente el archivo load.py sube los datos de la calificación
de riesgo a la base de datos en SQL
para su posterior uso y consumo dentro de la plataforma

Inputs: 

    'rs_df_combined.csv'

Outputs:

    actualiza la base de datos en la tabla tecnotrust_crime_data.rs_combined_ageb
