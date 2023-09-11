# <!><!> Script que carga los datos del índice de riesgo combinados a la base de datos

import psycopg2

root = '/data/'
file = 'rs_df_combined.csv'
POSTGRES_HOST = 'localhost'
POSTGRES_PORT = '5432'
POSTGRES_USERNAME = 'postgres'
POSTGRES_PASSWORD = ''
POSTGRES_DBNAME = 'postgres'

table_name = 'rs_combined_ageb'

create_table_query = f"""CREATE TABLE tecnotrust_crime_data.{table_name}(
                        ageb_id text PRIMARY KEY,
                        rs_all_2016 integer,
                        rs_all_2017 integer,
                        rs_all_2018 integer,
                        rs_all_2019 integer,
                        rs_all_2020 integer,
                        rs_all_2021 integer,
                        rs_all_last_12_months integer,
                        rs_all_6_months integer,
                        rs_all_3_months integer,
                        rs_all_historic integer,
                        actual_risk integer,
                        rs_all_2016_float float8,
                        rs_all_2017_float float8,
                        rs_all_2018_float float8,
                        rs_all_2019_float float8,
                        rs_all_2020_float float8,
                        rs_all_2021_float float8,
                        rs_all_last_12_months_float float8,
                        rs_all_6_months_float float8,
                        rs_all_3_months_float float8,
                        rs_all_historic_float float8,
                        actual_risk_float float8
                    )
                    """

def create_postgres_table(credentials,
                          table_name,
                          create_table_query,
                          csv_file_path):
    '''
    Función que sube los datos a una tabla en SQL - PostGres
    '''

    try:
        conn = psycopg2.connect(credentials)
        print("Connection success")

    except psycopg2.OperationalError:
        print("Incorrect database login information.")

    conn = psycopg2.connect(credentials)
    cur = conn.cursor()

    cur.execute(f"""DROP TABLE IF EXISTS tecnotrust_crime_data.{table_name}""")
    cur.execute(create_table_query)
    conn.commit()

    print("Table created")

    with open(csv_file_path, 'r') as f:
        next(f)
        cur.copy_from(f, f"""tecnotrust_crime_data.{table_name}""", sep=',')

    conn.commit()

    print("Done!")


def main():

    csv_file_path = root + file

    credentials = f"""
                    dbname = '{POSTGRES_DBNAME}'
                    user = '{POSTGRES_USERNAME}'
                    host = '{POSTGRES_HOST}'
                    port = '{POSTGRES_PORT}'
                    password = '{POSTGRES_PASSWORD}'
                   """

    create_postgres_table(credentials,
                          table_name,
                          create_table_query,
                          csv_file_path)

if __name__ == "__main__":
    main()
