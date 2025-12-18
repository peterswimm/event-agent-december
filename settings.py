from __future__ import annotations

from typing import Optional
from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""
    
    model_config = ConfigDict(env_file=".env", case_sensitive=False, extra="ignore")
    
    run_mode: Optional[str] = Field(default=None)
    api_token: Optional[str] = Field(default=None)
    app_insights_connection_string: Optional[str] = Field(default=None)
    
    # Microsoft Graph credentials
    graph_tenant_id: Optional[str] = Field(default=None)
    graph_client_id: Optional[str] = Field(default=None)
    graph_client_secret: Optional[str] = Field(default=None)
    
    # Microsoft Foundry (Azure AI) credentials
    foundry_project_endpoint: Optional[str] = Field(default=None)
    foundry_subscription_id: Optional[str] = Field(default=None)
    foundry_resource_group: Optional[str] = Field(default=None)
    foundry_project_name: Optional[str] = Field(default=None)
    foundry_model_deployment: str = Field(default="gpt-4o")
    
    # Feature flags
    graph_enabled: bool = Field(default=False)
    foundry_enabled: bool = Field(default=False)
    
    def validate_graph_ready(self) -> bool:
        """Check if all Graph credentials are configured."""
        return all([self.graph_tenant_id, self.graph_client_id, self.graph_client_secret])
    
    def validate_foundry_ready(self) -> bool:
        """Check if Microsoft Foundry credentials are configured."""
        return all([
            self.foundry_project_endpoint,
            self.foundry_subscription_id,
            self.foundry_resource_group,
            self.foundry_project_name
        ])
    
    def get_validation_errors(self) -> list[str]:
        """Return list of missing Graph credentials, if any."""
        errors = []
        if not self.graph_tenant_id:
            errors.append("GRAPH_TENANT_ID not set")
        if not self.graph_client_id:
            errors.append("GRAPH_CLIENT_ID not set")
        if not self.graph_client_secret:
            errors.append("GRAPH_CLIENT_SECRET not set")
        return errors
    
    def get_foundry_errors(self) -> list[str]:
        """Return list of missing Foundry credentials, if any."""
        errors = []
        if not self.foundry_project_endpoint:
            errors.append("FOUNDRY_PROJECT_ENDPOINT not set")
        if not self.foundry_subscription_id:
            errors.append("FOUNDRY_SUBSCRIPTION_ID not set")
        if not self.foundry_resource_group:
            errors.append("FOUNDRY_RESOURCE_GROUP not set")
        if not self.foundry_project_name:
            errors.append("FOUNDRY_PROJECT_NAME not set")
        return errors
