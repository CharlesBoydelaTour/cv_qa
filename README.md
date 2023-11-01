# CV QA Webapp

## Description

This webapp is a chatbot application hosted on Azure that answers questions about the owner's resume. The webapp uses Poetry for dependency management and Django as the web framework.

The website is accessible at : [charlesboydelatour.com](charlesboydelatour.com)

## Getting Started

### Prerequisites

- Python >= 3.11
- Poetry

### Installation

Install dependencies with Poetry:

```
poetry install
```

### Running the application

1. Activate the virtual environment:

```
poetry shell
```

2. Run the Django development server:

```
python manage.py runserver
```

3. The application should now be running on your local development server. Open your browser and navigate to `http://127.0.0.1:8000/` to use the chatbot.

## Deployment

This webapp is hosted on Azure with Azure App Service. It also uses Azure Cognitive Search to retrieve informations. Please refer to the Azure documentation for deployment instructions.
