terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }

  backend "azurerm" {

  }
}

provider "azurerm" {
  features {}

  subscription_id = "6a7b4057-b81c-4548-96c7-b7a5304b45a0"
}
