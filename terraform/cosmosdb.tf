data "azurerm_cosmosdb_account" "count_old" {
  name                = "count-cosmosdb"
  resource_group_name = "rg-tensora-count"
}

data "azurerm_cosmosdb_sql_database" "count_old" {
  name                = "tensora-count"
  resource_group_name = "rg-tensora-count"
  account_name        = data.azurerm_cosmosdb_account.count_old.name
}

resource "azurerm_cosmosdb_account" "count" {
  name                = "cosno-count-${var.customer}-${var.environment}"
  location            = var.location
  resource_group_name = "rg-count-${var.customer}-${var.environment}-storage"
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  consistency_policy {
    consistency_level = "Session"
  }

  geo_location {
    location          = var.location
    failover_priority = 0
  }

  capabilities {
    name = "EnableServerless"
  }
}

resource "azurerm_cosmosdb_sql_database" "count" {
  name                = "cosmos-count-${var.customer}-${var.environment}"
  resource_group_name = "rg-count-${var.customer}-${var.environment}-storage"
  account_name        = azurerm_cosmosdb_account.count.name
}

resource "azurerm_cosmosdb_sql_container" "predictions_container" {
  name                  = "predictions"
  resource_group_name   = "rg-count-${var.customer}-${var.environment}-storage"
  account_name          = azurerm_cosmosdb_account.count.name
  database_name         = azurerm_cosmosdb_sql_database.count.name
  partition_key_paths   = ["/project"]
  partition_key_version = 2
}

resource "azurerm_cosmosdb_sql_container" "projects_container" {
  name                  = "projects"
  resource_group_name   = "rg-count-${var.customer}-${var.environment}-storage"
  account_name          = azurerm_cosmosdb_account.count.name
  database_name         = azurerm_cosmosdb_sql_database.count.name
  partition_key_paths   = ["/id"]
  partition_key_version = 2
}
