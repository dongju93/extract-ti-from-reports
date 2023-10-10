import json
import os
from envs.env import json_path, output_path


def merge_json_files(directory):
    merged_data = []

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    merged_data.extend(data)
                elif isinstance(data, dict):
                    merged_data.append(data)
                else:
                    print(
                        f"Unexpected data structure in {filename}. Expected a list or dict but got {type(data)}."
                    )

    return merged_data


def sort_by_rule_id(data):
    return sorted(data, key=lambda x: x.get("rule_id", float("inf")))


directory_path = json_path
merged_data = merge_json_files(directory_path)
sorted_data = sort_by_rule_id(merged_data)

with open(
    output_path + "2015-2022_merged.json",
    "w",
) as outfile:
    json.dump(sorted_data, outfile, indent=4)
