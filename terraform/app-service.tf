resource "azurerm_container_registry" "count" {
  name                = "acrcount${var.customer}${var.environment}"
  resource_group_name = "rg-count-${var.customer}-${var.environment}-operations"
  location            = var.location
  sku                 = "Basic"
  admin_enabled       = true

  tags = {
    project_name = "Tensora Count"
    customer     = var.customer
    environment  = var.environment
  }
}

resource "azurerm_service_plan" "count" {
  name                = "asp-count-${var.customer}-${var.environment}-backend"
  resource_group_name = "rg-count-${var.customer}-${var.environment}-apps"
  location            = var.location

  os_type  = "Linux"
  sku_name = var.environment == "dev" ? "B1" : "P0v3"

  tags = {
    project_name = "Tensora Count"
    customer     = var.customer
    environment  = var.environment
  }
}

resource "azurerm_linux_web_app" "count_backend" {
  name                = "app-count-${var.customer}-${var.environment}-backend"
  resource_group_name = "rg-count-${var.customer}-${var.environment}-apps"
  location            = var.location
  service_plan_id     = azurerm_service_plan.count.id

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
      docker_image_name        = "count-${var.customer}-${var.environment}-backend:latest"
      docker_registry_url      = "https://${azurerm_container_registry.count.login_server}"
      docker_registry_username = azurerm_container_registry.count.admin_username
      docker_registry_password = azurerm_container_registry.count.admin_password
    }

    always_on                         = true
    ftps_state                        = "Disabled"
    health_check_path                 = "/api/v1/health"
    health_check_eviction_time_in_min = 2
  }

  app_settings = {
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = "false"
    WEBSITES_CONTAINER_START_LIMIT      = 1800
    WEBSITES_PORT                       = 8000
    API_KEY                             = var.api_key
    LOG_LEVEL                           = var.log_level
    // COSMOS_DB_ENDPOINT                  = azurerm_cosmosdb_account.count.endpoint
    // COSMOS_DB_PRIMARY_KEY               = azurerm_cosmosdb_account.count.primary_key
    // COSMOS_DB_DATABASE_NAME             = azurerm_cosmosdb_sql_database.count.name
    // AZURE_STORAGE_CONNECTION_STRING     = azurerm_storage_account.count.primary_blob_connection_string
    COSMOS_DB_ENDPOINT              = data.azurerm_cosmosdb_account.count_old.endpoint
    COSMOS_DB_PRIMARY_KEY           = data.azurerm_cosmosdb_account.count_old.primary_key
    COSMOS_DB_DATABASE_NAME         = data.azurerm_cosmosdb_sql_database.count_old.name
    AZURE_STORAGE_CONNECTION_STRING = data.azurerm_storage_account.count_old.primary_blob_connection_string
  }

  lifecycle {
    ignore_changes = [
      app_settings["DOCKER_REGISTRY_SERVER_PASSWORD"],
      site_config[0].application_stack[0].docker_registry_password
    ]
  }

  tags = {
    project_name = "Tensora Count"
    customer     = var.customer
    environment  = var.environment
  }
}
