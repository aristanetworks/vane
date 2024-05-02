import argparse
import os
import yaml

def create_master_def(test_catalog_dir):
    test_dir = os.walk(test_catalog_dir)

    tests_dict = {}
    for dir_path, _, catalog_files in test_dir:
        for catalog_file in catalog_files:
            if not catalog_file.endswith("-catalog.yml"):
                continue
            device = catalog_file.split("-catalog.yml")[0]
            file_path = f"{dir_path}/{catalog_file}"
            with open(file_path, "r", encoding="utf-8") as catalog_yml:
                tests = yaml.safe_load(catalog_yml)
            for key, value in tests.items():
                for test in value:
                    test_key = [a for a,b in test.items()][0]
                    vane_test = tests_dict.get(test_key, {})
                    vane_inputs = vane_test.get("inputs", {})
                    vane_device_inputs = vane_inputs.get(device, [])
                    anta_test_inputs = test[test_key]
                    vane_device_inputs.append(anta_test_inputs)
                    vane_inputs[device] = vane_device_inputs
                    vane_test["criteria"] = "name"
                    device_filter = vane_test.get("filter", {})
                    if not device_filter.get(device, ""):
                        device_filter[device] = device
                    vane_test["filter"] = device_filter
                    vane_test["inputs"] = vane_inputs
                    tests_dict[test_key] = vane_test

    with open('master_def.yaml', 'w') as master_file:
        yaml.dump({"testcase_data": tests_dict}, master_file)

def main():
    """main function"""

    args = parse_cli()

    if args.anta_test_catalog_dir:
        create_master_def(args.anta_test_catalog_dir[0])


def parse_cli():
    """Parse CLI options.

    Returns:
      args (obj): An object containing the CLI arguments.
    """

    parser = argparse.ArgumentParser(
        description=("Script to generate configs.yaml for vane from AVD structured data")
    )

    parser.add_argument(
        "--anta-test-catalog-dir",
        help="Point to anta test catalog dir",
        nargs=1,
        metavar=("anta_test_catalog_idr"),
    )
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    main()

