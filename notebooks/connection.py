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
    db_configs = {
        'oltp': config['CO_SA'],
        'etl': config['ETL_PRO'],
        'etl_or': config['ETL_PRO_OR']
    }

    engines = {key: create_engine(build_db_url(cfg)) for key, cfg in db_configs.items()}

    inspector_oltp = inspect(engines['oltp'])
    inspector_etl = inspect(engines['etl'])
    oltp_tables = inspector_oltp.get_table_names(schema=schema)
    etl_tables = inspector_etl.get_table_names()

    print(f"OLTP tables in schema '{schema}': {oltp_tables}")

    if not etl_tables:
        sql_scripts = load_config('../sqlscripts.yml')
        with engines['etl'].connect() as conn:
            for query in sql_scripts.values():
                conn.execute(text(query))
    return engines['oltp'], engines['etl'], engines['etl_or']