variable "subscription_id" {
  type        = string
  description = "The Azure subscription id"
}

variable "location" {
  type        = string
  description = "The Azure location for all resources"
}

variable "customer" {
  type        = string
  description = "The name of the customer"
}

variable "environment" {
  type        = string
  description = "Environment to deploy the resources (e.g. pro, dev etc.)"
}

variable "api_key" {
  type        = string
  description = "Valid API Key for authentication"
}

variable "log_level" {
  type        = string
  description = "Log level for the application"
  default     = "INFO"
}
