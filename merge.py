import json
import os
from envs.env import json_path, output_path


def merge_json_files(directory):
    merged_data = []

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), "r") as f:
                data = json.load(f)
                merged_data.append(data)

    return merged_data


directory_path = json_path
merged_data = merge_json_files(directory_path)

with open(
    output_path + "2015-2022_merged.json",
    "w",
) as outfile:
    json.dump(merged_data, outfile, indent=4)
