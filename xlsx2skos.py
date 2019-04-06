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

	return parser.parse_args(args)
	
def load_data(args):
	''' Cargar los datos desde el archivo Excel.'''
	
	workbook = xlrd.open_workbook(args.source)
	if args.tab is None:
		worksheet = workbook.sheet_by_index(0)
	else:
		worksheet = workbook.sheet_by_name(args.tab)
	num_rows = worksheet.nrows

	metadata = {
			"namespace": worksheet.cell_value(0, 1)
		}
	concepts = []
	for row in range(3, num_rows):
		concepts.append({
					"uri": worksheet.cell_value(row, 0),
					"definition_es": worksheet.cell_value(row, 1) or None,
					"prefLabel_es": worksheet.cell_value(row, 2) or None,
					"prefLabel_en": worksheet.cell_value(row, 3) or None,
					"broader": worksheet.cell_value(row, 4) or None
				})

	return { "metadata": metadata, "concepts": concepts }


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