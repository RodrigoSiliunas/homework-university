from setuptools import setup, find_packages

"""
==========================================================================
 ➠ Backend of Twitter
 ➠ Section By: Fabricio Abreu
 ➠ Related system: Core da aplicação do Twitter
==========================================================================
"""

# Informações sobre o autor
author_name = "Fabricio Abreu"
author_email = "fabricioabbreu7@gmail.com"

setup(
    name="twitter-clone-fuck-elon-mickey-mouse",  # Nome do pacote
    version="0.1.0",  # Versão inicial do projeto
    author=author_name,
    author_email=author_email,
    description="Uma aplicação Python que clona funcionalidades básicas do Twitter. Feito em FastAPI.",
    packages=find_packages(),  # Localiza automaticamente o pacote APP e evita erro de importação circular
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.12',  # Requisito de versão mínima do Python
)