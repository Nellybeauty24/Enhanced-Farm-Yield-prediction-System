import json

notebook_path2 = 'train_yield_colab_v2.ipynb'
with open(notebook_path2, 'r') as f:
    nb2 = json.load(f)

for cell in nb2['cells']:
    if cell['cell_type'] == 'code' and any("X = df.drop(columns=" in line for line in cell['source']):
        source_str = "".join(cell['source'])
        target_line = "X = df.drop(columns=[target_col, 'region', 'state', 'pest_type', 'pest_severity', 'labor_input', 'farm_size_ha', 'rainfall_variability', 'extreme_weather', 'temperature_stress', 'soil_degradation'], errors='ignore')"
        lines = source_str.split("\n")
        new_lines = []
        for line in lines:
            if "X = df.drop(columns=" in line:
                new_lines.append(target_line)
            else:
                new_lines.append(line)
        cell['source'] = [line + "\n" for line in new_lines]
        if cell['source'][-1] == "\n":
            cell['source'].pop()
        else:
            cell['source'][-1] = cell['source'][-1].rstrip("\n")

with open(notebook_path2, 'w') as f:
    json.dump(nb2, f, indent=1)
print("Updated train_yield_colab_v2.ipynb drop columns list")
