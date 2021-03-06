import sys
import argparse
import xlrd
import pandas as pd
from jinja2 import Environment, PackageLoader, select_autoescape


DESCRIPTION = '''
Genera un vocabulario SKOS a partir de un archivo XLSX.
El archivo XLSX debe seguir la plantilla ubicada en templates/plantilla.xlsx
'''

def parse_args(args):
	'''Hacer parsing de los argumentos recibidos por línea de comando.'''
	
	parser = argparse.ArgumentParser(description=DESCRIPTION)
	parser.add_argument("source",
						metavar="ORIGEN",
						help="Nombre del archivo entrada")
	parser.add_argument("-t",
						"--tab",
						metavar="PESTAÑA",
						help="Nombre de la pestaña a leer en el archivo de entrada. Por defecto se lee la primera pestaña.")
	parser.add_argument("target",
						metavar="DESTINO",
						help="Nombre del archivo XML de salida")
	parser.add_argument("-f",
						"--template_file",
						help="Nombre del archivo de plantilla. Default: skos-xl.xml",
						default="skos-xl.xml",
						metavar="<filename>")
	parser.add_argument("-d",
						"--template_dir",
						help="Nombre de la carpeta de plantillas. Default: templates",
						default="templates",
						metavar="<dirname>")
	parser.add_argument("-m",
						"--term",
						help="Incluir term en índices",
						default=False, 
						action='store_true')	

	return parser.parse_args(args)
	
def load_data(args):
	''' Cargar los datos desde el archivo Excel.'''
	
	workbook = xlrd.open_workbook(args.source)
	if args.tab is None:
		worksheet = workbook.sheet_by_index(0)
	else:
		worksheet = workbook.sheet_by_name(args.tab)
	num_rows = worksheet.nrows
	
	metadata = dict()
	for row in range(6):
		metadata[worksheet.cell_value(row, 0)] = worksheet.cell_value(row, 1)
		metadata['term'] = args.term

	concepts = []
	for row in range(8, num_rows):
		concept = {
					"term": worksheet.cell_value(row, 0),
					"uri": metadata["preffix"] + worksheet.cell_value(row, 0),
					"definition_es": worksheet.cell_value(row, 1) or None,
					"prefLabel_es": worksheet.cell_value(row, 2) or None,
					"prefLabel_en": worksheet.cell_value(row, 3) or None,
					"broader": worksheet.cell_value(row, 4) or None,
					"children": []
				}
		concepts.append(concept)

	index = {}
	for i in range(len(concepts)):
		index[concepts[i]["term"]] = i

	for concept in concepts:
		if concept["broader"] is not None:
			concepts[index[concept["broader"]]]["children"].append(concept)

	tree = []
	for concept in concepts:
		if concept["broader"] is None:
			tree.append(concept)

	return { "metadata": metadata, "concepts": concepts, "tree": tree }


def render(args, data_dict):
	'''Escribir datos en archivo de salida usando plantilla.'''
	env = Environment(
		loader=PackageLoader('xlsx2skos', args.template_dir),
		autoescape=select_autoescape(['html', 'xml'])
	)
	template = env.get_template(args.template_file)
	rendered_text = template.render(**data_dict).encode("utf-8")
	with open(args.target, 'wb') as f:
		f.write(rendered_text)
	return


def main(args = sys.argv[1:]):
	args = parse_args(args)
	data_dict = load_data(args)
	render(args, data_dict)	

if __name__ == '__main__':
    main()