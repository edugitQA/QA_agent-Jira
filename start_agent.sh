#!/bin/bash

# Ativa o ambiente virtual (se estiver usando)
# source venv/bin/activate

# Inicia o agente de QA
python3 src/main.py "$@"
