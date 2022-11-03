# pdfapi

# Main Project files:
pdf - django site
pdfapi - fastapi api

# venv
https://www.geeksforgeeks.org/create-virtual-environment-using-venv-python/
https://www.youtube.com/watch?v=APOPm01BVrk&ab_channel=CoreySchafer

Steps to create and use a venv:
    create venv : python -m venv folder_name
    activate using - venvpdfapi\Scripts\activate.bat from a cmd prompt.
    pip freeze > requirements.txt

Create a new Django site:
    Once venv is created, inside virtual directory run - pip install django
    check if django was installed properly using "django-admin"
    Then, start a project by "django-admin startproject calculator ."  dot is to create a single folder.
    To use different port to run the server - python manage.py runserver 9000 , once executed check if the localsite is up and running.
    STart an app. To start an app run "python manage.py startapp abcd"
    Once an app is created register it by adding it to Installed Apps in settings.py of the created project folder.
# Auth

https://itsjoshcampos.codes/fast-api-api-key-authorization#heading-setup-an-api-key-environment-variable
https://testdriven.io/tips/6840e037-4b8f-4354-a9af-6863fb1c69eb/

# Prod checklist:

Hide /docs and schema details:
app = FastAPI(swagger_ui_parameters={"defaultModelsExpandDepth": -1}, docs_url=None)

# Links
#https://medium.com/geekculture/communicate-via-json-payload-and-upload-files-in-fastapi-244bdbc447dd
#https://stackoverflow.com/questions/71516140/fastapi-runs-api-calls-in-serial-instead-of-parallel-fashion/71517830#71517830
# https://fastapi.tiangolo.com/async/#path-operation-functions
#https://medium.com/geekculture/communicate-via-json-payload-and-upload-files-in-fastapi-244bdbc447dd

# Docs
https://squidfunk.github.io/mkdocs-material/