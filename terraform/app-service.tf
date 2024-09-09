resource "azurerm_container_registry" "tensora_count" {
  name                = "crcount${var.environment}001"
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "Basic"
  admin_enabled       = true
}

resource "azurerm_service_plan" "profiles" {
  name                = "asp-profiles-backend-${var.environment}-001"
  resource_group_name = var.resource_group_name
  location            = var.location

  os_type  = "Linux"
  sku_name = var.environment == "prd" ? "P0v3" : "B1"
}

resource "azurerm_linux_web_app" "tensora_count_backend" {
  name                = "tensora-count-backend-${var.environment}"
  resource_group_name = var.resource_group_name
  location            = var.location
  service_plan_id     = azurerm_service_plan.profiles.id

  logs {
    application_logs {
      file_system_level = "Verbose"
    }
    http_logs {
      file_system {
        retention_in_days = 14
        retention_in_mb   = 100
      }
    }
  }

  site_config {
    application_stack {
      docker_image_name        = "tensora-count-backend:${var.environment}"
      docker_registry_url      = "https://${azurerm_container_registry.profiles.login_server}"
      docker_registry_username = azurerm_container_registry.profiles.admin_username
      docker_registry_password = azurerm_container_registry.profiles.admin_password
    }

    always_on                         = true
    ftps_state                        = "Disabled"
    health_check_path                 = "/api/v1/"
    health_check_eviction_time_in_min = 2
  }

  app_settings = {
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = "false"
    WEBSITES_CONTAINER_START_LIMIT      = 1800
    WEBSITES_PORT                       = 8000
    PROJECT_NAME                        = var.project_name
    API_BASE_URL                        = var.api_base_url
    COSMOS_DB_ENDPOINT                  = var.COSMOS_DB_ENDPOINT
    COSMOS_DB_PRIMARY_KEY               = var.COSMOS_DB_PRIMARY_KEY
    COSMOS_DB_DATABASE_NAME             = var.COSMOS_DB_DATABASE_NAME
  }

  lifecycle {
    ignore_changes = [
      app_settings["DOCKER_REGISTRY_SERVER_PASSWORD"],
      site_config[0].application_stack[0].docker_registry_password
    ]
  }

  tags = {
    environment = var.environment
  }
}
