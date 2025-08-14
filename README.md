# HTTP-Methods-Extractor

## Overview
**HTTP-Methods-Extractor** is a lightweight tool that scans your source code files and extracts the HTTP methods (`GET`, `POST`, `PUT`, `DELETE`, etc.) used in your API endpoints.

Simply provide the local file path of your source code, and the extractor will parse it to list all HTTP methods defined in your code.

---

## Features

- Currently, the extractor supports **Java (Spring Boot)** only, but future versions will include support for other backend frameworks and languages such as **Python (Flask/Django/FastAPI)**, **Node.js (Express)**, and more.

    - Extracts HTTP methods from Java Spring Boot controller files.
    - Supports common annotations such as:
    - `@GetMapping`
    - `@PostMapping`
    - `@PutMapping`
    - `@DeleteMapping`
    - `@RequestMapping(method = RequestMethod.XYZ)`
    
- Simple CLI usage.
- Lightweight and fast.

---
