import os
import re
from openpyxl import Workbook

http_methods = {
    'GetMapping': 'GET',
    'PostMapping': 'POST',
    'PutMapping': 'PUT',
    'DeleteMapping': 'DELETE'
}

pattern_single = re.compile(r'@(?P<method>\w+Mapping)\s*\(\s*(?:value\s*=\s*)?"?(?P<path>[^",)]+)')
pattern_request_mapping = re.compile(r'@RequestMapping\s*\(.*method\s*=\s*RequestMethod\.(?P<method>\w+).*value\s*=\s*"(?P<path>[^"]+)"')
pattern_constant = re.compile(r'public\s+static\s+final\s+String\s+(\w+)\s*=\s*"([^"]+)"')
pattern_description = re.compile(r'@Operation\s*\(\s*description\s*=\s*"([^"]+)"')

def extract_constants_from_all_files(directory):
    constants = {}
    for root, _, files in os.walk(directory):
        for name in files:
            if name.endswith('.java'):
                with open(os.path.join(root, name), 'r', encoding='utf-8') as f:
                    for line in f:
                        match = pattern_constant.search(line)
                        if match:
                            constants[match.group(1)] = match.group(2)
    return constants

def extract_api_info(file_path, constants):
    apis = []
    current_description = None

    with open(file_path, 'r', encoding='utf-8') as file:
        for line_num, line in enumerate(file, 1):
            match_desc = pattern_description.search(line)
            if match_desc:
                current_description = match_desc.group(1).strip()

            match = pattern_single.search(line)
            if match:
                method = http_methods.get(match.group('method'))
                path = match.group('path')

                if not path.startswith("/"):
                    path = constants.get(path, f"<Unresolved: {path}>")

                apis.append((method, path, current_description or ""))
                current_description = None

            else:
                match = pattern_request_mapping.search(line)
                if match:
                    method = match.group('method')
                    path = match.group('path')
                    if not path.startswith("/"):
                        path = constants.get(path, f"<Unresolved: {path}>")
                    apis.append((method, path, current_description or ""))
                    current_description = None

    return apis

def scan_multiple_directories(directories):
    all_apis = []
    all_constants = {}

    for directory in directories:
        constants = extract_constants_from_all_files(directory)
        all_constants.update(constants)

    for directory in directories:
        for root, _, files in os.walk(directory):
            for name in files:
                if name.endswith('.java'):
                    path = os.path.join(root, name)
                    apis = extract_api_info(path, all_constants)
                    all_apis.extend(apis)

    return all_apis

def write_to_excel(data, output_file='HTTP_Methods_called_by_api_list.xlsx'):
    wb = Workbook()
    ws = wb.active
    ws.title = "API List"
    ws.append(["Method", "API Endpoint", "Description"]) #It will give you table with columns: Method, API Endpoint and Description.

    for method, path, desc in data:
        ws.append([method, path, desc])

    wb.save(output_file)
    print(f"Excel file saved as '{output_file}'.")

if __name__ == "__main__":
    controller_dirs = [
        r"#Path to the code file",
        #Paste location of java code file from any repository.
    ]

    api_data = scan_multiple_directories(controller_dirs)
    write_to_excel(api_data)