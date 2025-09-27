#!/bin/bash

# Production Triple Store Setup Script
# Sets up a working Fuseki triple store with proper ontology loading

set -e

FUSEKI_URL="http://localhost:3030"
DATASET_NAME="semantic-model"
SCHEMAS_DIR="schemas"

echo "🔧 Setting up production triple store..."

# Wait for Fuseki to be ready
echo "⏳ Waiting for Fuseki..."
timeout=30
counter=0
until curl -s "$FUSEKI_URL/$/ping" > /dev/null; do
  if [ $counter -ge $timeout ]; then
    echo "❌ Timeout waiting for Fuseki"
    exit 1
  fi
  sleep 1
  counter=$((counter + 1))
done

echo "✅ Fuseki is ready"

# Create dataset via web interface
echo "📊 Creating dataset: $DATASET_NAME"
curl -s -X POST "$FUSEKI_URL/$/datasets" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "dbName=$DATASET_NAME&dbType=tdb2" > /dev/null

# Verify dataset creation
if curl -s "$FUSEKI_URL/$/stats/$DATASET_NAME" | grep -q "dataset"; then
  echo "✅ Dataset created successfully"
else
  echo "❌ Dataset creation failed"
  exit 1
fi

# Download Gist if needed
if [ ! -f "$SCHEMAS_DIR/gist-core.ttl" ]; then
  echo "📥 Downloading Gist ontology..."
  curl -L "https://w3id.org/semanticarts/ontology/gistCore" \
       -H "Accept: text/turtle" \
       -o "$SCHEMAS_DIR/gist-core.ttl"
  echo "✅ Gist downloaded"
fi

# Load ontologies in order
echo "📚 Loading ontologies..."

# 1. Gist (Level 1)
echo "  Loading Gist..."
curl -s -X POST "$FUSEKI_URL/$DATASET_NAME/data" \
  -H "Content-Type: text/turtle" \
  --data-binary "@$SCHEMAS_DIR/gist-core.ttl" > /dev/null

# 2. DBC Bridge (Level 2)
echo "  Loading DBC Bridge..."
curl -s -X POST "$FUSEKI_URL/$DATASET_NAME/data" \
  -H "Content-Type: application/rdf+xml" \
  --data-binary "@$SCHEMAS_DIR/ontologies/gist_dbc_bridge.owl" > /dev/null

# 3. SOW Inference Rules (Level 3a)
echo "  Loading SOW Inference Rules..."
curl -s -X POST "$FUSEKI_URL/$DATASET_NAME/data" \
  -H "Content-Type: application/rdf+xml" \
  --data-binary "@$SCHEMAS_DIR/sow/ontologies/sow_inference_rules.owl" > /dev/null

# 4. Complete SOW (Level 3b)
echo "  Loading Complete SOW..."
curl -s -X POST "$FUSEKI_URL/$DATASET_NAME/data" \
  -H "Content-Type: application/rdf+xml" \
  --data-binary "@$SCHEMAS_DIR/sow/ontologies/complete_sow_ontology.owl" > /dev/null

# 5. Test instances
echo "  Loading test instances..."
curl -s -X POST "$FUSEKI_URL/$DATASET_NAME/data" \
  -H "Content-Type: text/turtle" \
  --data-binary "@$SCHEMAS_DIR/test-data/minimal_semantic_validation.ttl" > /dev/null

echo "✅ All ontologies loaded"

# Test basic connectivity
echo "🔍 Testing SPARQL connectivity..."

# Count triples
TRIPLE_COUNT=$(curl -s -G "$FUSEKI_URL/$DATASET_NAME/sparql" \
  --data-urlencode "query=SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }" \
  -H "Accept: application/sparql-results+json" | \
  python3 -c "import sys, json; result = json.load(sys.stdin); print(result['results']['bindings'][0]['count']['value'])" 2>/dev/null || echo "0")

echo "📊 Dataset contains $TRIPLE_COUNT triples"

# Test cross-level query
echo "🔗 Testing 4-level connectivity..."
CONNECTIVITY_RESULT=$(curl -s -G "$FUSEKI_URL/$DATASET_NAME/sparql" \
  --data-urlencode "query=PREFIX gist: <https://w3id.org/semanticarts/ontology/gistCore#>
PREFIX bridge: <https://agentic-data-scraper.com/ontology/gist-dbc-bridge#>
PREFIX csow: <https://agentic-data-scraper.com/ontology/complete-sow#>
SELECT (COUNT(*) as ?count) WHERE {
  ?org a gist:Organization .
  ?canvas a bridge:DataBusinessCanvas .
  ?sow a csow:SemanticStatementOfWork .
  ?contract a bridge:DataContract .
}" \
  -H "Accept: application/sparql-results+json" | \
  python3 -c "import sys, json; result = json.load(sys.stdin); print(result['results']['bindings'][0]['count']['value'])" 2>/dev/null || echo "0")

if [ "$CONNECTIVITY_RESULT" -gt "0" ]; then
  echo "✅ Cross-level connectivity working"
else
  echo "⚠️  Cross-level connectivity not fully established"
fi

echo ""
echo "🎉 Production triple store setup complete!"
echo ""
echo "📋 Access Information:"
echo "  • Fuseki Web UI:    $FUSEKI_URL"
echo "  • SPARQL Endpoint:  $FUSEKI_URL/$DATASET_NAME/sparql"
echo "  • Dataset Stats:    $FUSEKI_URL/\$/stats/$DATASET_NAME"
echo ""
echo "🔧 Test Commands:"
echo "  • Count triples:    curl -G '$FUSEKI_URL/$DATASET_NAME/sparql' --data-urlencode 'query=SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }'"
echo "  • List classes:     curl -G '$FUSEKI_URL/$DATASET_NAME/sparql' --data-urlencode 'query=SELECT DISTINCT ?class WHERE { ?s a ?class } ORDER BY ?class'"