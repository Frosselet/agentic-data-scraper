#!/bin/bash
# Validate submodule integration and dependencies

set -e

echo "🔍 Validating submodule integration..."

# Check submodule structure
echo "📁 Checking submodule structure..."
for module in ontologies core agents contracts collectors pipelines deployment; do
    if [ -L "$module" ]; then
        echo "✅ $module -> $(readlink $module)"
    else
        echo "❌ $module missing or not a symlink"
        exit 1
    fi
done

# Check .gitmodules configuration
echo "📝 Validating .gitmodules..."
if [ -f ".gitmodules" ]; then
    echo "✅ .gitmodules file exists"
    echo "📋 Configured submodules:"
    grep "path = " .gitmodules | sed 's/^[[:space:]]*/  /'
else
    echo "❌ .gitmodules file missing"
    exit 1
fi

# Check dependency hierarchy
echo "🔗 Validating dependency hierarchy..."
dependencies=(
    "ontologies:foundation"
    "core:depends_on_ontologies"
    "agents:depends_on_core_ontologies"
    "contracts:depends_on_core_ontologies"
    "collectors:depends_on_core_ontologies"
    "pipelines:depends_on_all_above"
    "deployment:depends_on_pipelines"
)

for dep in "${dependencies[@]}"; do
    module="${dep%%:*}"
    desc="${dep##*:}"
    if [ -d "$module" ]; then
        echo "✅ $module ($desc)"
    else
        echo "❌ $module missing"
        exit 1
    fi
done

# Check CLAUDE.md files
echo "📚 Checking CLAUDE.md files..."
for module in ontologies core agents contracts collectors pipelines deployment; do
    if [ -f "$module/CLAUDE.md" ]; then
        echo "✅ $module/CLAUDE.md exists"
    else
        echo "❌ $module/CLAUDE.md missing"
    fi
done

echo "🎉 Integration validation completed successfully!"