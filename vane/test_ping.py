"""Traffic Flow using Ping command"""
import logging
import configparser
import sys
import pyeapi
import yaml


logging.basicConfig(
    level=logging.INFO,
    filename="run_ping.log",
    filemode="w",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def run_ping_command():
    """Traffic Flow using Ping command"""
    definitions_file = sys.argv[1]
    dut_name = sys.argv[2]
    loopback_ip = sys.argv[3]
    repeat_ping = sys.argv[4]

    with open(definitions_file, "r", encoding="utf-8") as input_yaml:
        yaml_data = yaml.safe_load(input_yaml)

    logging.info("Starting Traffic Flow")

    config_1 = configparser.ConfigParser()
    config_1.read(yaml_data["parameters"]["eapi_file"])
    conf = config_1["connection:" + dut_name]
    conn = pyeapi.connect(
        transport=conf["transport"],
        host=conf["host"],
        username=conf["username"],
        password=conf["password"],
        timeout=600,
        return_node=True,
    )
    show_command = ["ping " + loopback_ip + " repeat " + repeat_ping]
    output = conn.enable(show_command)

    logging.info(f"Traffic flow ended: {output} ")
    print(output)


run_ping_command()
