import yaml
from sqlalchemy import create_engine, inspect, text

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def connect(schema):
    config = load_config('../config_fill.yml')
    config_co = config['CO_SA']
    config_etl = config['ETL_PRO']
    config_etl_or = config['ETL_PRO_OR']

    url_co = (f"{config_co['drivername']}://{config_co['user']}:{config_co['password']}@{config_co['host']}:"
              f"{config_co['port']}/{config_co['dbname']}")
    url_etl = (f"{config_etl['drivername']}://{config_etl['user']}:{config_etl['password']}@{config_etl['host']}:"
               f"{config_etl['port']}/{config_etl['dbname']}")
    url_etl_or = (f"{config_etl_or['drivername']}://{config_etl_or['user']}:{config_etl_or['password']}@{config_etl_or['host']}:"
                  f"{config_etl_or['port']}/{config_etl_or['dbname']}")

    co_oltp = create_engine(url_co)
    etl_conn = create_engine(url_etl)
    etl_conn_or = create_engine(url_etl_or)

    inspector2 = inspect(co_oltp)
    inspector = inspect(etl_conn)
    tnames = inspector.get_table_names()
    tnames2 = inspector2.get_table_names(schema=schema)

    print(tnames2)
    if not tnames:
        with etl_conn.connect() as conn:
            with open('../sqlscripts.yml', 'r') as f:
                sql = yaml.safe_load(f)
                for key, val in sql.items():
                    conn.execute(text(val))
            conn.commit()
    return co_oltp, etl_conn, etl_conn_or