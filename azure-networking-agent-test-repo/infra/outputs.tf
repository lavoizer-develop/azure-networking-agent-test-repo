output "hub_vnet_id" {
  value = azurerm_virtual_network.hub.id
}

output "app_vnet_id" {
  value = azurerm_virtual_network.app.id
}

output "storage_account_name" {
  value = azurerm_storage_account.app.name
}

output "key_vault_name" {
  value = azurerm_key_vault.app.name
}
