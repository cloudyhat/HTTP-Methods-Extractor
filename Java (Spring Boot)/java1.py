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
pattern_request_mapping = re.compile(
    r'@RequestMapping\s*\(\s*([^)]*)\)', re.DOTALL
)
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

def extract_closest_description(desc_matches, annot_pos):
    for i, desc in enumerate(desc_matches):
        if desc.start() < annot_pos:
            return desc.group(1)
    return ""

def extract_api_info(file_path, constants):
    apis = []

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    for match in re.finditer(r'@(?P<method>\w+Mapping)\s*\(\s*(?:value\s*=\s*)?"?(?P<path>[^",)\s]+)', content):
        method = http_methods.get(match.group('method'))
        path = match.group('path')
        if not path.startswith("/"):
            path = constants.get(path, f"<Unresolved: {path}>")
        if method:
            apis.append((method, path))

    for match in pattern_request_mapping.finditer(content):
        params = match.group(1)

        method_match = re.search(r'method\s*=\s*RequestMethod\.(\w+)', params)
        path_match = re.search(r'(?:path|value)\s*=\s*"([^"]+)"', params)

        if method_match and path_match:
            method = method_match.group(1)
            path = path_match.group(1)
            if not path.startswith("/"):
                path = constants.get(path, f"<Unresolved: {path}>")
            if method:
                apis.append((method, path))

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
    ws.title = "API List with Methods"
    ws.append(["Method", "API Endpoint"]) #It will give you table with columns: Method and API Endpoint.

    for method, path in data:
        ws.append([method, path])

    wb.save(output_file)
    print(f"Excel file saved as '{output_file}'.")

if __name__ == "__main__":
    controller_dirs = [
        r"#Path to the code file",
        #Paste location of java code file from any repository.
    ]
    api_data = scan_multiple_directories(controller_dirs)
    write_to_excel(api_data)