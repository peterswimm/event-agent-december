"""
Tier 3 & 4 Integration Examples

Working code samples for Azure AI Foundry and Power Platform integrations.
Run individual examples or combine them for full enterprise setup.
"""

import asyncio
import os
from pathlib import Path


# ===== TIER 3: AZURE AI FOUNDRY EXAMPLES =====

async def example_foundry_basic_extraction():
    """Example 1: Use Foundry model for extraction"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Foundry Model Extraction")
    print("="*60)

    from integrations import create_foundry_provider

    # Create provider
    provider = create_foundry_provider(
        project_connection_string=os.getenv("FOUNDRY_CONNECTION_STRING"),
        model_name="gpt-4-turbo"
    )

    # Print model info
    print(f"\nUsing: {provider.get_model_info()}")

    # Sample extraction
    system_prompt = """Extract research paper metadata in JSON format:
    - title
    - authors
    - abstract
    - key_findings
    - confidence (0.0-1.0)"""

    user_prompt = """Title: Deep Learning for Computer Vision
Authors: Smith et al.
Abstract: This paper presents novel architectures for image classification...
Key findings: Achieved 98% accuracy on ImageNet."""

    result = await provider.extract(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.3
    )

    print(f"\nExtraction Result:\n{result}")


async def example_foundry_model_selection():
    """Example 2: Auto-select model by artifact type"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Auto Model Selection by Artifact Type")
    print("="*60)

    from integrations import FoundryModelRegistry

    artifact_types = ["paper", "talk", "repository"]

    for artifact_type in artifact_types:
        model = FoundryModelRegistry.get_recommended_model(artifact_type)
        info = FoundryModelRegistry.get_model(model)
        print(f"\n{artifact_type.upper()}: {model}")
        print(f"  Description: {info['description']}")
        print(f"  Use cases: {', '.join(info['use_cases'])}")


def example_foundry_agent_registration():
    """Example 3: Register tools in Foundry"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Register Extraction Tools in Foundry")
    print("="*60)

    from integrations import FoundryAgentIntegration
    import json

    integration = FoundryAgentIntegration(
        project_connection_string=os.getenv("FOUNDRY_CONNECTION_STRING")
    )

    # Register tools
    tools = integration.register_extraction_tools()
    print(f"\nRegistering {len(tools)} tools:")
    for tool in tools:
        print(f"\n✓ {tool['name']}")
        print(f"  Description: {tool['description']}")
        print(f"  Required params: {tool['input_schema']['required']}")


def example_foundry_deployment_config():
    """Example 4: Get deployment configuration"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Get Deployment Configuration")
    print("="*60)

    from integrations import FoundryAgentIntegration
    import json

    integration = FoundryAgentIntegration(
        project_connection_string=os.getenv("FOUNDRY_CONNECTION_STRING")
    )

    # Create agent
    agent_config = integration.create_foundry_agent()
    print(f"\nAgent Configuration:")
    print(json.dumps(agent_config, indent=2))

    # Get deployment config
    deploy_config = integration.get_deployment_config(
        replicas=3,
        cpu="2",
        memory="8G"
    )
    print(f"\nDeployment Configuration:")
    print(json.dumps(deploy_config, indent=2))


def example_foundry_evaluation():
    """Example 5: Evaluate extraction quality"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Evaluate Extraction Quality")
    print("="*60)

    from integrations import FoundryEvaluation
    import json

    evaluation = FoundryEvaluation(
        project_connection_string=os.getenv("FOUNDRY_CONNECTION_STRING")
    )

    # Get metrics
    metrics = evaluation.get_built_in_metrics()
    print(f"\nAvailable Metrics ({len(metrics)}):")
    for metric in metrics:
        print(f"  • {metric['name']}: {metric['description']}")

    # Evaluate extraction
    result = evaluation.evaluate_extraction(
        artifact_id="paper_123",
        extracted_content="Generated abstract and methods...",
        source_content="Original full paper content...",
        metrics=["coherence", "groundedness", "relevance"]
    )

    print(f"\nEvaluation Results:")
    print(json.dumps(result, indent=2))


def example_foundry_batch_evaluation():
    """Example 6: Batch evaluate multiple extractions"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Batch Evaluation")
    print("="*60)

    from integrations import FoundryEvaluation
    import json

    evaluation = FoundryEvaluation(
        project_connection_string=os.getenv("FOUNDRY_CONNECTION_STRING")
    )

    # Sample extractions
    extractions = [
        {
            "id": "paper_1",
            "content": "Extracted content for paper 1",
            "source": "Full paper 1 content"
        },
        {
            "id": "talk_1",
            "content": "Extracted content for talk 1",
            "source": "Full talk 1 transcript"
        },
        {
            "id": "repo_1",
            "content": "Extracted content for repo 1",
            "source": "Full repo 1 analysis"
        }
    ]

    # Batch evaluate
    results = evaluation.batch_evaluate(extractions)

    print(f"\nBatch Evaluation Summary:")
    print(f"  Total Evaluated: {results['total_evaluated']}")
    print(f"  Average Scores:")
    for metric, score in results['average_scores'].items():
        print(f"    • {metric}: {score:.2f}")


def example_foundry_performance_summary():
    """Example 7: Get performance summary"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Performance Summary & Trends")
    print("="*60)

    from integrations import FoundryEvaluation
    import json

    evaluation = FoundryEvaluation(
        project_connection_string=os.getenv("FOUNDRY_CONNECTION_STRING")
    )

    # Get summary
    summary = evaluation.get_performance_summary(time_range_days=30)

    print(f"\nPerformance Summary (Last 30 Days):")
    print(f"  Total Extractions: {summary['summary']['total_extractions']}")
    print(f"  Successful: {summary['summary']['successful']}")
    print(f"  Success Rate: {summary['summary']['success_rate']:.1%}")
    print(f"\n  Average Quality Scores:")
    for metric, score in summary['average_metrics'].items():
        print(f"    • {metric}: {score:.2f}")
    print(f"\n  Top Performers:")
    for artifact_type, score in summary['top_performers'].items():
        print(f"    • {artifact_type}: {score:.2f}")


# ===== TIER 4: POWER PLATFORM EXAMPLES =====

async def example_power_platform_server():
    """Example 8: Start Power Platform connector server"""
    print("\n" + "="*60)
    print("EXAMPLE 8: Start Power Platform Connector")
    print("="*60)

    from integrations import create_power_platform_connector
    import uvicorn

    # Create connector app
    app = create_power_platform_connector(
        enable_foundry=os.getenv("FOUNDRY_ENABLED", "false").lower() == "true"
    )

    port = int(os.getenv("API_PORT", 8000))
    print(f"\n✓ Power Platform Connector created")
    print(f"✓ Listening on http://localhost:{port}")
    print(f"\nAvailable Endpoints:")
    print(f"  POST   /extract - Extract from artifact")
    print(f"  GET    /artifacts - List artifacts")
    print(f"  GET    /search - Search artifacts")
    print(f"  POST   /artifacts/{{id}}/feedback - Submit feedback")
    print(f"  GET    /analytics/summary - Power BI summary")
    print(f"  GET    /health - Health check")
    print(f"\nTo start server:")
    print(f"  python -m integrations.power_platform_connector")

    # Uncomment to actually run:
    # uvicorn.run(app, host="0.0.0.0", port=port)


async def example_power_automate_extraction():
    """Example 9: Simulate Power Automate call"""
    print("\n" + "="*60)
    print("EXAMPLE 9: Simulate Power Automate Extraction")
    print("="*60)

    from integrations import ExtractionRequest, ExtractionResponse
    import json

    # Simulate Power Automate request
    request = ExtractionRequest(
        artifact_type="paper",
        source_location="/path/to/paper.pdf",
        save_results=True,
        notify_teams=False
    )

    print(f"\nPower Automate Request:")
    print(json.dumps(request.dict(), indent=2))

    # Simulated response
    response = ExtractionResponse(
        success=True,
        title="Deep Learning for Computer Vision",
        confidence=0.88,
        overview="This paper presents novel architectures...",
        artifact_url="https://storage.azure.com/artifacts/paper.json",
        extraction_time_seconds=12.5
    )

    print(f"\nPower Automate Response:")
    print(json.dumps(response.dict(), indent=2))


def example_power_apps_artifact_list():
    """Example 10: Simulate Power Apps artifact list"""
    print("\n" + "="*60)
    print("EXAMPLE 10: Power Apps - List Artifacts")
    print("="*60)

    from integrations import ArtifactItem
    import json
    from datetime import datetime

    # Simulate artifact list response
    artifacts = [
        ArtifactItem(
            id="artifact_1",
            title="Deep Learning Advances",
            overview="Novel approaches to neural network architecture...",
            confidence=0.89,
            source_type="paper",
            extraction_date=datetime.utcnow().isoformat(),
            contributor_count=3
        ),
        ArtifactItem(
            id="artifact_2",
            title="Enterprise AI in Practice",
            overview="Real-world deployment considerations...",
            confidence=0.85,
            source_type="talk",
            extraction_date=datetime.utcnow().isoformat(),
            contributor_count=1
        )
    ]

    print(f"\nArtifacts for Power Apps:")
    for artifact in artifacts:
        print(f"\n  {artifact.title}")
        print(f"    ID: {artifact.id}")
        print(f"    Type: {artifact.source_type}")
        print(f"    Confidence: {artifact.confidence:.2f}")


def example_power_bi_analytics():
    """Example 11: Power BI analytics data"""
    print("\n" + "="*60)
    print("EXAMPLE 11: Power BI Analytics")
    print("="*60)

    import json
    from datetime import datetime

    # Simulate analytics response
    analytics = {
        "timestamp": datetime.utcnow().isoformat(),
        "summary": {
            "total_extractions": 1250,
            "successful_extractions": 1198,
            "success_rate": 0.958,
            "average_confidence": 0.87
        },
        "by_type": {
            "paper": {
                "count": 450,
                "success_rate": 0.96,
                "avg_confidence": 0.89,
                "daily_trend": [45, 48, 42, 50, 46]
            },
            "talk": {
                "count": 550,
                "success_rate": 0.95,
                "avg_confidence": 0.85,
                "daily_trend": [55, 52, 58, 60, 53]
            },
            "repository": {
                "count": 250,
                "success_rate": 0.97,
                "avg_confidence": 0.86,
                "daily_trend": [25, 28, 22, 26, 24]
            }
        }
    }

    print(f"\nPower BI Analytics Data:")
    print(json.dumps(analytics, indent=2))


def example_extended_settings():
    """Example 12: Extended settings configuration"""
    print("\n" + "="*60)
    print("EXAMPLE 12: Extended Settings Configuration")
    print("="*60)

    from integrations import get_settings
    import json

    settings = get_settings()

    print(f"\nActive Integration Providers:")
    providers = settings.get_active_providers()
    for provider in providers:
        print(f"  ✓ {provider}")

    print(f"\nIntegration Tier: {settings.get_integration_tier()}")

    print(f"\nCapabilities Summary:")
    summary = settings.get_capability_summary()
    print(json.dumps(summary, indent=2))

    print(f"\nValidation Results:")
    foundry_ok = settings.validate_foundry_config()
    power_ok = settings.validate_power_platform_config()
    m365_ok = settings.validate_m365_config()

    print(f"  {'✓' if foundry_ok else '✗'} Foundry Configuration")
    print(f"  {'✓' if power_ok else '✗'} Power Platform Configuration")
    print(f"  {'✓' if m365_ok else '✗'} M365 Configuration")


# ===== RUNNER =====

async def run_async_examples():
    """Run async examples"""
    print("\n" + "="*60)
    print("ASYNC EXAMPLES")
    print("="*60)

    if os.getenv("FOUNDRY_CONNECTION_STRING"):
        try:
            await example_foundry_basic_extraction()
        except Exception as e:
            print(f"Skipping: {e}")

        try:
            await example_power_automate_extraction()
        except Exception as e:
            print(f"Skipping: {e}")
    else:
        print("\nSkipping async examples (FOUNDRY_CONNECTION_STRING not set)")


def run_sync_examples():
    """Run synchronous examples"""
    print("\n" + "="*60)
    print("SYNCHRONOUS EXAMPLES")
    print("="*60)

    # Foundry examples
    try:
        example_foundry_model_selection()
    except Exception as e:
        print(f"Skipping: {e}")

    try:
        if os.getenv("FOUNDRY_CONNECTION_STRING"):
            example_foundry_agent_registration()
            example_foundry_deployment_config()
            example_foundry_evaluation()
            example_foundry_batch_evaluation()
            example_foundry_performance_summary()
    except Exception as e:
        print(f"Skipping Foundry examples: {e}")

    # Power Platform examples
    try:
        example_power_platform_server()
        example_power_apps_artifact_list()
        example_power_bi_analytics()
    except Exception as e:
        print(f"Skipping Power Platform examples: {e}")

    # Settings example
    try:
        example_extended_settings()
    except Exception as e:
        print(f"Skipping settings example: {e}")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("TIER 3 & 4 INTEGRATION EXAMPLES")
    print("="*60)

    # Run sync examples
    run_sync_examples()

    # Run async examples
    print("\n")
    asyncio.run(run_async_examples())

    print("\n" + "="*60)
    print("EXAMPLES COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("  1. Set FOUNDRY_CONNECTION_STRING to test Foundry integration")
    print("  2. Run: python -m integrations.power_platform_connector")
    print("  3. Create Power Automate flow pointing to connector")
    print("  4. Build Power Apps UI consuming /artifacts endpoint")
    print("  5. Set up Power BI dashboard with /analytics endpoints")


if __name__ == "__main__":
    main()
