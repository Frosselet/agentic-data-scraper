"""
CLI launcher for Data Business Canvas Streamlit app

Provides command-line interface to launch the Data Business Canvas application
following the ADR-012 framework implementation.
"""

import typer
import subprocess
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = typer.Typer(
    name="canvas",
    help="Data Business Canvas - Build your data strategy foundation",
    add_completion=False
)


@app.command("start")
def start_canvas(
    port: int = typer.Option(8501, "--port", "-p", help="Port to run Streamlit app"),
    host: str = typer.Option("localhost", "--host", "-h", help="Host to bind to"),
    browser: bool = typer.Option(True, "--browser/--no-browser", help="Open browser automatically"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode")
):
    """
    Launch the Data Business Canvas Streamlit application.

    The Data Business Canvas helps you define your data strategy using the 9+3 framework:
    - 9 Core Business Model Elements (Value Props, Customers, etc.)
    - 3 Data-Specific Elements (Sources, Governance, Technology)

    This creates the foundation for intelligent data discovery.
    """

    typer.echo("🎯 Starting Data Business Canvas...")
    typer.echo(f"   URL: http://{host}:{port}")
    typer.echo("   Press Ctrl+C to stop")

    # Path to the streamlit app
    canvas_app_path = Path(__file__).parent.parent / "ui" / "data_business_canvas.py"

    if not canvas_app_path.exists():
        typer.echo(f"❌ Canvas app not found at: {canvas_app_path}", err=True)
        raise typer.Exit(1)

    # Build streamlit command
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(canvas_app_path),
        "--server.port", str(port),
        "--server.address", host,
        "--server.headless", str(not browser).lower(),
        "--browser.gatherUsageStats", "false"
    ]

    if debug:
        cmd.extend(["--logger.level", "debug"])

    try:
        # Run streamlit
        logger.info(f"Launching streamlit with command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)

    except KeyboardInterrupt:
        typer.echo("\n👋 Data Business Canvas stopped")
    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ Failed to start Canvas: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(1)


@app.command("discover")
def start_discovery_flow(
    port: int = typer.Option(8502, "--port", "-p", help="Port to run Streamlit app"),
    host: str = typer.Option("localhost", "--host", "-h", help="Host to bind to"),
    browser: bool = typer.Option(True, "--browser/--no-browser", help="Open browser automatically"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode")
):
    """
    Launch the integrated Discovery Flow application.

    This combines the Data Business Canvas with BAML-powered data discovery
    to provide intelligent source recommendations based on your business context.
    """

    typer.echo("🔍 Starting Discovery Flow...")
    typer.echo(f"   URL: http://{host}:{port}")
    typer.echo("   Press Ctrl+C to stop")

    # Path to the discovery flow app
    flow_app_path = Path(__file__).parent.parent / "ui" / "discovery_flow.py"

    if not flow_app_path.exists():
        typer.echo(f"❌ Discovery flow app not found at: {flow_app_path}", err=True)
        raise typer.Exit(1)

    # Build streamlit command
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(flow_app_path),
        "--server.port", str(port),
        "--server.address", host,
        "--server.headless", str(not browser).lower(),
        "--browser.gatherUsageStats", "false"
    ]

    if debug:
        cmd.extend(["--logger.level", "debug"])

    try:
        # Run streamlit
        logger.info(f"Launching discovery flow with command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)

    except KeyboardInterrupt:
        typer.echo("\n👋 Discovery Flow stopped")
    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ Failed to start Discovery Flow: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(1)


@app.command("validate")
def validate_canvas(
    canvas_file: Path = typer.Argument(help="Path to canvas JSON file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """
    Validate a saved Data Business Canvas JSON file.

    Checks for:
    - Required fields completion
    - Business logic consistency
    - Data source feasibility
    - Compliance requirements
    """

    if not canvas_file.exists():
        typer.echo(f"❌ Canvas file not found: {canvas_file}", err=True)
        raise typer.Exit(1)

    typer.echo(f"🔍 Validating canvas: {canvas_file}")

    try:
        import json
        from ..ui.data_business_canvas import DataBusinessCanvas

        # Load canvas data
        with open(canvas_file, 'r', encoding='utf-8') as f:
            canvas_data = json.load(f)

        # Create canvas instance and validate
        canvas = DataBusinessCanvas()
        canvas.canvas_data = canvas_data

        validation_results = canvas._validate_canvas()

        if validation_results["is_valid"]:
            typer.echo("✅ Canvas validation passed!")
            typer.echo(f"   Completion: {validation_results['completion_score']:.1%}")
        else:
            typer.echo("⚠️  Canvas validation issues found:")
            for issue in validation_results["issues"]:
                typer.echo(f"   • {issue}")

            if verbose:
                typer.echo(f"\nCompletion score: {validation_results['completion_score']:.1%}")

    except Exception as e:
        typer.echo(f"❌ Validation failed: {e}", err=True)
        raise typer.Exit(1)


@app.command("export")
def export_to_sow(
    canvas_file: Path = typer.Argument(help="Path to canvas JSON file"),
    output_file: Path = typer.Option(None, "--output", "-o", help="Output SOW file path"),
    format: str = typer.Option("json", help="Output format: json, yaml, txt")
):
    """
    Export Data Business Canvas to SOW (Statement of Work) format.

    Converts the canvas data into a structured SOW that can be used
    by the BAML agents for data discovery and pipeline generation.
    """

    if not canvas_file.exists():
        typer.echo(f"❌ Canvas file not found: {canvas_file}", err=True)
        raise typer.Exit(1)

    if output_file is None:
        output_file = canvas_file.with_suffix(f".sow.{format}")

    typer.echo(f"📄 Exporting canvas to SOW: {output_file}")

    try:
        import json
        import asyncio
        from ..ui.data_business_canvas import DataBusinessCanvas

        # Load canvas data
        with open(canvas_file, 'r', encoding='utf-8') as f:
            canvas_data = json.load(f)

        # Create canvas instance
        canvas = DataBusinessCanvas()
        canvas.canvas_data = canvas_data

        # Generate SOW
        if asyncio.run(canvas._generate_sow_draft()):
            typer.echo("✅ SOW generated successfully!")

            # Save in requested format
            if format == "json":
                # JSON format already handled by the canvas
                pass
            elif format == "txt":
                sow_text = canvas._canvas_to_sow_text()
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(sow_text)
            else:
                typer.echo(f"❌ Unsupported format: {format}", err=True)
                raise typer.Exit(1)

            typer.echo(f"📁 SOW saved to: {output_file}")
        else:
            typer.echo("❌ Failed to generate SOW", err=True)
            raise typer.Exit(1)

    except Exception as e:
        typer.echo(f"❌ Export failed: {e}", err=True)
        raise typer.Exit(1)


@app.command("info")
def show_info():
    """Show information about the Data Business Canvas framework."""

    typer.echo("""
🎯 Data Business Canvas Framework

The Data Business Canvas extends the traditional Business Model Canvas with
data-specific elements to help you build a comprehensive data strategy.

📊 Framework Structure (9+3):

Core Business Elements (9):
  1. Value Propositions - What data value you create
  2. Customer Segments - Who benefits from data insights
  3. Customer Relationships - How you engage data consumers
  4. Channels - How insights are delivered
  5. Key Activities - Core data operations
  6. Key Resources - Essential data assets
  7. Key Partners - External data/service providers
  8. Cost Structure - Data operation costs
  9. Revenue Streams - Value monetization

Data-Specific Elements (+3):
  10. Data Sources - Where data originates
  11. Data Governance - Compliance and quality control
  12. Technology Infrastructure - Technical enablers

🔗 Integration with Agentic Data Scraper:

The canvas provides business context that guides:
  • BAML-powered data discovery agents
  • Semantic source recommendations
  • SOW generation and validation
  • Data contract enforcement
  • Quality threshold setting

📚 Learn More:
  • docs/adr/ADR-011-business-model-canvas-integration.md
  • docs/adr/ADR-012-data-business-canvas-ontological-foundation.md

🚀 Quick Start:
  agentic-data-scraper canvas start
""")


if __name__ == "__main__":
    app()