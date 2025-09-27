#!/bin/bash

# Create Working Triple Store - Production Foundation Setup
# This script establishes a working semantic infrastructure foundation

set -e

FUSEKI_URL="http://localhost:3030"
DATASET_NAME="ds"

echo "🔧 Creating Production Semantic Infrastructure Foundation"
echo "======================================================"

# Wait for Fuseki
echo "⏳ Waiting for Fuseki..."
timeout=30
counter=0
until curl -s "$FUSEKI_URL/$/ping" > /dev/null; do
  if [ $counter -ge $timeout ]; then
    echo "❌ Fuseki not accessible"
    exit 1
  fi
  sleep 1
  counter=$((counter + 1))
done
echo "✅ Fuseki accessible"

# Create dataset using admin credentials
echo "📊 Creating dataset: $DATASET_NAME"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
  "http://admin:admin123@localhost:3030/\$/datasets" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "dbName=$DATASET_NAME&dbType=tdb2")

if [ "$RESPONSE" = "200" ] || [ "$RESPONSE" = "409" ]; then
  echo "✅ Dataset ready"
else
  echo "❌ Dataset creation failed (HTTP $RESPONSE)"
  exit 1
fi

# Test SPARQL endpoint
echo "🔍 Testing SPARQL endpoint..."
SPARQL_RESPONSE=$(curl -s -G "$FUSEKI_URL/$DATASET_NAME/sparql" \
  --data-urlencode "query=ASK { ?s ?p ?o }" \
  -H "Accept: application/sparql-results+json")

SPARQL_TEST=$(echo "$SPARQL_RESPONSE" | \
  python3 -c "import sys, json; result = json.load(sys.stdin); print('working' if 'boolean' in result else 'failed')" 2>/dev/null || echo "failed")

if [ "$SPARQL_TEST" = "working" ]; then
  echo "✅ SPARQL endpoint working"
else
  echo "❌ SPARQL endpoint test failed"
  echo "Response: $SPARQL_RESPONSE"
  exit 1
fi

# Load ontologies
echo "📚 Loading ontologies..."

# Check if ontologies exist
ONTOLOGIES=(
  "schemas/ontologies/core/gist-core.ttl:text/turtle"
  "schemas/ontologies/bridge/gist_dbc_bridge.owl:application/rdf+xml"
  "schemas/ontologies/sow/sow_inference_rules.owl:application/rdf+xml"
  "schemas/ontologies/sow/complete_sow_ontology.owl:application/rdf+xml"
  "schemas/validation/minimal_semantic_validation.ttl:text/turtle"
)

LOADED_COUNT=0
for ONTOLOGY_INFO in "${ONTOLOGIES[@]}"; do
  IFS=':' read -r FILE_PATH CONTENT_TYPE <<< "$ONTOLOGY_INFO"

  if [ -f "$FILE_PATH" ]; then
    echo "  Loading $FILE_PATH..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
      "http://admin:admin123@localhost:3030/$DATASET_NAME/data" \
      -H "Content-Type: $CONTENT_TYPE" \
      --data-binary "@$FILE_PATH")

    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
      echo "    ✅ Loaded successfully"
      LOADED_COUNT=$((LOADED_COUNT + 1))
    else
      echo "    ❌ Failed (HTTP $HTTP_CODE)"
    fi
  else
    echo "    ⚠️  File not found: $FILE_PATH"
  fi
done

echo "📊 Loaded $LOADED_COUNT ontologies"

# Final validation
echo "🔍 Final validation..."

# Count triples
TRIPLE_COUNT=$(curl -s -G "$FUSEKI_URL/$DATASET_NAME/sparql" \
  --data-urlencode "query=SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }" \
  -H "Accept: application/sparql-results+json" | \
  python3 -c "import sys, json; result = json.load(sys.stdin); print(result['results']['bindings'][0]['count']['value'])" 2>/dev/null || echo "0")

echo "📊 Total triples: $TRIPLE_COUNT"

# Test semantic query
SEMANTIC_TEST=$(curl -s -G "$FUSEKI_URL/$DATASET_NAME/sparql" \
  --data-urlencode "query=PREFIX gist: <https://w3id.org/semanticarts/ontology/gistCore#>
SELECT (COUNT(*) as ?count) WHERE { ?s a gist:Organization }" \
  -H "Accept: application/sparql-results+json" | \
  python3 -c "import sys, json; result = json.load(sys.stdin); print(result['results']['bindings'][0]['count']['value'])" 2>/dev/null || echo "0")

echo "🏢 Gist Organizations: $SEMANTIC_TEST"

if [ "$TRIPLE_COUNT" -gt "100" ] && [ "$SEMANTIC_TEST" -gt "0" ]; then
  echo ""
  echo "🎉 PRODUCTION SEMANTIC INFRASTRUCTURE FOUNDATION ESTABLISHED"
  echo ""
  echo "📋 Access Information:"
  echo "  • Fuseki Web UI:    $FUSEKI_URL"
  echo "  • SPARQL Endpoint:  $FUSEKI_URL/$DATASET_NAME/sparql"
  echo "  • Dataset Stats:    $FUSEKI_URL/\$/stats/$DATASET_NAME"
  echo ""
  echo "🔧 Test Query:"
  echo "  curl -G '$FUSEKI_URL/$DATASET_NAME/sparql' \\"
  echo "    --data-urlencode 'query=SELECT * WHERE { ?s a ?type } LIMIT 10'"
  echo ""
  echo "✅ Foundation ready for semantic applications"
  exit 0
else
  echo "❌ Foundation validation failed"
  echo "   Triples: $TRIPLE_COUNT (expected >100)"
  echo "   Organizations: $SEMANTIC_TEST (expected >0)"
  exit 1
fi