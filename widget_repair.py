import nbformat
import os

def clean_widgets_metadata(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=nbformat.NO_CONVERT)

    if 'widgets' in nb['metadata']:
        del nb['metadata']['widgets']
        with open(notebook_path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
        print(f"Cleaned: {notebook_path}")
    else:
        print(f"No widgets metadata in: {notebook_path}")

# Walk through the directory and clean all ipynb files
for root, _, files in os.walk('.'):
    for file in files:
        if file.endswith('.ipynb'):
            clean_widgets_metadata(os.path.join(root, file))
