# Schema Organization

This directory contains all schemas, ontologies, and data models for the Agentic Data Scraper platform, organized in a clean, logical structure.

## 📁 Directory Structure

```
schemas/
├── 📁 ontologies/          # Semantic Web ontologies (.owl, .ttl)
│   ├── 📁 core/           # Foundation ontologies (GIST, RDF)
│   ├── 📁 bridge/         # Data Business Canvas bridge layer
│   ├── 📁 sow/           # Statement of Work ontologies
│   └── 📁 domain/        # Domain-specific ontologies
├── 📁 contracts/          # Data contracts and templates
│   ├── 📁 templates/     # JSON Schema templates for SOW, contracts
│   └── 📁 contexts/      # Business domain contexts
├── 📁 agents/            # Agent schemas and data models
│   ├── 📁 baml_src/      # BAML agent definitions (.baml)
│   └── 📁 python/       # Python data models (Pydantic)
├── 📁 validation/        # Test data and validation schemas
└── 📁 docs/             # Schema documentation
```

## 🎯 Schema Categories

### Ontologies (`/ontologies/`)
**Purpose**: Semantic Web ontologies defining the knowledge graph structure

- **Core**: Foundation ontologies (GIST Core, RDF Schema)
- **Bridge**: Data Business Canvas to GIST bridge layer
- **SOW**: Statement of Work and contract ontologies
- **Domain**: Specific domains (power generation, maritime logistics)

### Contracts (`/contracts/`)
**Purpose**: Data contract templates and business contexts

- **Templates**: JSON Schema templates for SOW and data contracts
- **Contexts**: Business domain context definitions (finance, supply chain, commodities)

### Agents (`/agents/`)
**Purpose**: Agent definitions and data models

- **BAML**: Agent behavior definitions in BAML format
- **Python**: Pydantic data models and validation schemas

### Validation (`/validation/`)
**Purpose**: Test data and validation schemas

- Contains minimal test ontologies for CI/CD validation

## 🔗 Integration Points

### BAML Agent Generation
```bash
# Generate Python client from BAML schemas
cd schemas/agents/baml_src
uv run baml-cli generate
```

### Fuseki Triple Store Loading
```bash
# Load ontologies into Fuseki (uses new paths)
./scripts/create_working_triple_store.sh
```

### Python Import Paths
```python
# Import schemas from new location
from schemas.agents.python.sow import SOWContract
from schemas.agents.python.scraped_data import ScrapedData
```

## 📋 Migration Guide

### Old vs New Paths

| Old Path | New Path | Type |
|----------|----------|------|
| `baml_src/` | `schemas/agents/baml_src/` | BAML agents |
| `src/agentic_data_scraper/schemas/` | `schemas/agents/python/` | Python models |
| `schemas/sow/ontologies/` | `schemas/ontologies/sow/` | OWL ontologies |
| `schemas/sow/contexts/` | `schemas/contracts/contexts/` | JSON contexts |
| `schemas/test-data/` | `schemas/validation/` | Test schemas |

### Updated References
All scripts, documentation, and configuration files have been updated to use the new paths.

## 🛠️ Development Workflow

1. **Add new ontology**: Place in appropriate `/ontologies/` subdirectory
2. **Update agent behavior**: Modify BAML files in `/agents/baml_src/`
3. **Add data models**: Create Python schemas in `/agents/python/`
4. **Test changes**: Use validation schemas in `/validation/`
5. **Document**: Update schemas in `/docs/`

## ✅ Benefits

- **Single Source of Truth**: All schemas in one organized location
- **Clear Separation**: Different types in logical directories
- **Easy Discovery**: Developers know exactly where to find schemas
- **Scalable**: Easy to add new domains and agent types
- **Clean Dependencies**: Clear import hierarchy