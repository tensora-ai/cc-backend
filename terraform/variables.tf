variable "location" {
  type        = string
  description = "The Azure location for all resources"
}

variable "resource_group_name" {
  type        = string
  description = "The name of the Azure resource group"
}

variable "environment" {
  type        = string
  description = "Environment to deploy the resources (e.g. pro, dev etc.)"
}

variable "project_name" {
  type        = string
  description = "Name of the project"
}

variable "api_base_url" {
  type    = string
  default = "Base URL of the Profiles API"
}

variable "COSMOS_DB_ENDPOINT" {
  type    = string
  default = "Base URL of the CosmosDB Endpoint"
}

variable "COSMOS_DB_PRIMARY_KEY" {
  type    = string
  default = "Primary Key for the CosmosDB"
}

variable "COSMOS_DB_DATABASE_NAME" {
  type    = string
  default = "Database Name of the relevant Cosmos Database"
}

