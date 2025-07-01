import csv
import json
import os

def csv_to_flat_json(csv_dir, json_filepath, limit=50):
    files = ['Dataset.csv']

    flat_data = []

    for file in files:
        path = os.path.join(csv_dir, file)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    if i >= limit:
                        break
                    row['__source_file__'] = file.replace('.csv', '')  # Optional: to track where each row came from
                    flat_data.append(row)
        except FileNotFoundError:
            print(f"Missing file: {file}, skipping...")
        except Exception as e:
            print(f"Error reading {file}: {e}")

    # Save to JSON
    try:
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(flat_data, f, indent=4)
        print(f"✅ Flat data saved to {json_filepath}")
    except Exception as e:
        print(f"Error writing JSON: {e}")

# Example usage
csv_dir = 'csv'
json_filepath = 'output/newDataset.json'
csv_to_flat_json(csv_dir, json_filepath)
