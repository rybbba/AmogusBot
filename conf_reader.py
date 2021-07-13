import configparser

def read_conf(path: str) -> configparser.ConfigParser:
    parser = configparser.ConfigParser()
    parser.read(path)
    return parser
