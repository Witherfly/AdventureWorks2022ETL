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

    print(oltp_tables)
    if not etl_tables:
        with engines['etl'].connect() as conn:
            with open('../sqlscripts.yml', 'r') as f:
                sql = yaml.safe_load(f)
                for key, val in sql.items():
                    conn.execute(text(val))
            conn.commit()
    return engines['oltp'], engines['etl'], engines['etl_or']