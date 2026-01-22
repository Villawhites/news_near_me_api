import os

def create_project_structure():
    project_name = "news_near_me_api"
    
    # Definición de la estructura: directorios y archivos base
    structure = {
        "app": [
            "__init__.py",
            "main.py",
        ],
        "app/core": ["__init__.py", "config.py", "security.py"],
        "app/api/v1/endpoints": ["__init__.py", "users.py", "news.py"],
        "app/api/v1": ["__init__.py", "api.py"],
        "app/crud": ["__init__.py"],
        "app/models": ["__init__.py"],
        "app/schemas": ["__init__.py"],
        "app/services": ["__init__.py"],
        "app/db": ["__init__.py", "base.py", "session.py"],
        "tests": ["__init__.py", "test_main.py"],
    }

    # Archivos en la raíz
    root_files = [".env", ".gitignore", "requirements.txt", "README.md"]

    # Crear el directorio raíz del proyecto
    if not os.path.exists(project_name):
        os.makedirs(project_name)
        print(f"🚀 Creando proyecto: {project_name}")

    # Crear subdirectorios y archivos internos
    for folder, files in structure.items():
        folder_path = os.path.join(project_name, folder)
        os.makedirs(folder_path, exist_ok=True)
        
        for file in files:
            file_path = os.path.join(folder_path, file)
            with open(file_path, "w") as f:
                if file == "main.py":
                    f.write("from fastapi import FastAPI\n\napp = FastAPI(title='News Near Me API')\n\n@app.get('/')\ndef read_root():\n    return {'message': 'Welcome to News Near Me API'}\n")
                else:
                    f.write("") # Crea archivo vacío o con placeholder
    
    # Crear archivos de raíz
    for file in root_files:
        file_path = os.path.join(project_name, file)
        with open(file_path, "w") as f:
            if file == ".gitignore":
                f.write("__pycache__/\n.env\nvenv/\n*.pyc\n")
            elif file == "requirements.txt":
                f.write("fastapi\nuvicorn[standard]\npydantic[email]\nsqlalchemy\nalembic\npython-dotenv\n")
            else:
                f.write("")

    print(f"✅ ¡Estructura creada con éxito en ./{project_name}!")

if __name__ == "__main__":
    create_project_structure()
