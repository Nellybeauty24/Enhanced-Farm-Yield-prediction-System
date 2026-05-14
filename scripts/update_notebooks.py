import json

# 1. Update Crop Classifier Notebook
with open('train_in_colab.ipynb', 'r') as f:
    crop_nb = json.load(f)

for cell in crop_nb['cells']:
    if cell['cell_type'] == 'code':
        new_source = []
        for line in cell['source']:
            if "'region', 'state', 'agro_zone', 'soil_type'," in line:
                new_source.append("        'agro_zone', 'soil_type', \n")
            else:
                new_source.append(line)
        cell['source'] = new_source

with open('train_in_colab_v2.ipynb', 'w') as f:
    json.dump(crop_nb, f, indent=1)


# 2. Update Yield Regressor Notebook
with open('train_yield_colab.ipynb', 'r') as f:
    yield_nb = json.load(f)

for cell in yield_nb['cells']:
    if cell['cell_type'] == 'code':
        new_source = []
        for line in cell['source']:
            if "X = df.drop(columns=[target_col])" in line:
                new_source.append("X = df.drop(columns=[target_col, 'region', 'state'], errors='ignore')\n")
            else:
                new_source.append(line)
        cell['source'] = new_source

with open('train_yield_colab_v2.ipynb', 'w') as f:
    json.dump(yield_nb, f, indent=1)

print("Created train_in_colab_v2.ipynb and train_yield_colab_v2.ipynb")
