output "cosmos_db_endpoint" {
  description = "The endpoint of the Cosmos database"
  value       = azurerm_cosmosdb_account.db_account.endpoint
}

output "app_service_endpoint" {
  description = "The endpoint of the app service hosting the Profiles backend"
  value       = azurerm_linux_web_app.profiles_backend.default_hostname
}

