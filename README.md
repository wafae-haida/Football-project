# Football Multi-Agent System

## Description

Système multi-agent pour la détection des événements clés d’un match de football.

Le système repose sur plusieurs agents spécialisés qui collaborent pour préparer les données, extraire des caractéristiques, entraîner des modèles et détecter les événements clés d’un match.

## Architecture

* Data Processing Agent
* Action Analysis Agent
* Spatial Analysis Agent
* Graph Analysis Agent
* Training Agent

## Dataset

* Source : StatsBomb
* Format : JSON
* Split :

  * Train : 70%
  * Validation : 15%
  * Test : 15%

## Installation

```bash
pip install -r requirements.txt
```

## Exécution

Exemple :

```bash
jupyter notebook
```

Puis exécuter les notebooks ou les crews correspondants.

## Structure

```text
multi_agent_system/
dataset/
models/
```
