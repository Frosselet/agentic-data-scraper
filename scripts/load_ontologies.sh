#!/bin/bash

# Load Ontologies into Fuseki Triple Store
# This script loads the complete Gist-DBC-SOW-Contract ontology hierarchy

set -e

FUSEKI_URL="http://fuseki:3030"
SCHEMAS_DIR="/schemas"

echo "🚀 Loading Agentic Data Scraper Semantic Model into Fuseki..."
echo "Fuseki URL: $FUSEKI_URL"

# Wait for Fuseki to be ready
echo "⏳ Waiting for Fuseki to be ready..."
until curl -s "$FUSEKI_URL/$/ping" > /dev/null; do
  echo "Waiting for Fuseki..."
  sleep 2
done
echo "✅ Fuseki is ready!"

# Function to load RDF file into dataset
load_rdf() {
    local file=$1
    local dataset=$2
    local graph_name=$3

    echo "📥 Loading $file into dataset $dataset..."

    if [ -f "$file" ]; then
        # Load into named graph
        curl -X POST \
             -H "Content-Type: text/turtle" \
             --data-binary "@$file" \
             "$FUSEKI_URL/$dataset/data?graph=$graph_name"

        if [ $? -eq 0 ]; then
            echo "✅ Successfully loaded $file"
        else
            echo "❌ Failed to load $file"
            exit 1
        fi
    else
        echo "⚠️  File not found: $file"
    fi
}

# Load Gist Upper Ontology (download if needed)
echo "🔽 Downloading Gist ontology..."
if [ ! -f "$SCHEMAS_DIR/gist-core.ttl" ]; then
    curl -L "https://w3id.org/semanticarts/ontology/gistCore" \
         -H "Accept: text/turtle" \
         -o "$SCHEMAS_DIR/gist-core.ttl"
fi

# Load ontologies into the ontologies-only dataset
echo "📚 Loading ontologies into ontologies dataset..."

# 1. Load Gist (Level 1)
if [ -f "$SCHEMAS_DIR/gist-core.ttl" ]; then
    load_rdf "$SCHEMAS_DIR/gist-core.ttl" "ontologies" "https://w3id.org/semanticarts/ontology/gistCore"
fi

# 2. Load DBC Bridge (Level 2)
if [ -f "$SCHEMAS_DIR/ontologies/gist_dbc_bridge.owl" ]; then
    load_rdf "$SCHEMAS_DIR/ontologies/gist_dbc_bridge.owl" "ontologies" "https://agentic-data-scraper.com/ontology/gist-dbc-bridge"
fi

# 3. Load SOW Inference Rules (Level 3a)
if [ -f "$SCHEMAS_DIR/sow/ontologies/sow_inference_rules.owl" ]; then
    load_rdf "$SCHEMAS_DIR/sow/ontologies/sow_inference_rules.owl" "ontologies" "https://agentic-data-scraper.com/ontology/sow"
fi

# 4. Load Complete SOW Ontology (Level 3b)
if [ -f "$SCHEMAS_DIR/sow/ontologies/complete_sow_ontology.owl" ]; then
    load_rdf "$SCHEMAS_DIR/sow/ontologies/complete_sow_ontology.owl" "ontologies" "https://agentic-data-scraper.com/ontology/complete-sow"
fi

# Load the same ontologies into main gist-dbc-sow dataset
echo "📚 Loading ontologies into main gist-dbc-sow dataset..."

if [ -f "$SCHEMAS_DIR/gist-core.ttl" ]; then
    load_rdf "$SCHEMAS_DIR/gist-core.ttl" "gist-dbc-sow" "https://w3id.org/semanticarts/ontology/gistCore"
fi

if [ -f "$SCHEMAS_DIR/ontologies/gist_dbc_bridge.owl" ]; then
    load_rdf "$SCHEMAS_DIR/ontologies/gist_dbc_bridge.owl" "gist-dbc-sow" "https://agentic-data-scraper.com/ontology/gist-dbc-bridge"
fi

if [ -f "$SCHEMAS_DIR/sow/ontologies/sow_inference_rules.owl" ]; then
    load_rdf "$SCHEMAS_DIR/sow/ontologies/sow_inference_rules.owl" "gist-dbc-sow" "https://agentic-data-scraper.com/ontology/sow"
fi

if [ -f "$SCHEMAS_DIR/sow/ontologies/complete_sow_ontology.owl" ]; then
    load_rdf "$SCHEMAS_DIR/sow/ontologies/complete_sow_ontology.owl" "gist-dbc-sow" "https://agentic-data-scraper.com/ontology/complete-sow"
fi

echo "🎉 Ontology loading complete!"

# Verify loaded data
echo "🔍 Verifying loaded ontologies..."

# Count triples in each dataset
for dataset in "ontologies" "gist-dbc-sow"; do
    echo "📊 Triple count in $dataset:"
    curl -s -G "$FUSEKI_URL/$dataset/sparql" \
         --data-urlencode "query=SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }" \
         -H "Accept: application/sparql-results+json" | \
         python3 -c "import sys, json; print('  Triples:', json.load(sys.stdin)['results']['bindings'][0]['count']['value'])"
done

echo "🏁 Setup complete! Access Fuseki at http://localhost:3030"
echo "📝 Main datasets:"
echo "   - http://localhost:3030/gist-dbc-sow    (Complete connected model)"
echo "   - http://localhost:3030/ontologies      (Ontologies only)"
echo "   - http://localhost:3030/test-data       (Test instances)"