resource "azurerm_resource_group" "this" {
  name     = "rg-${var.prefix}-cc"
  location = var.location

  tags = {
    environment = "test"
    purpose     = "github-copilot-agent-demo"
  }
}
