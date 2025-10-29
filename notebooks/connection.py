import yaml
from sqlalchemy import create_engine, inspect, text

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def build_db_url(config):
    return (
        f"{config['drivername']}://{config['user']}:{config['password']}@"
        f"{config['host']}:{config['port']}/{config['dbname']}"
    )

def connect(schema):
    config = load_config('../config_fill.yml')
    config_co = config['CO_SA']
    config_etl = config['ETL_PRO']
    config_etl_or = config['ETL_PRO_OR']

    url_co = build_db_url(config_co)
    url_etl = build_db_url(config_etl)
    url_etl_or = build_db_url(config_etl_or)

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