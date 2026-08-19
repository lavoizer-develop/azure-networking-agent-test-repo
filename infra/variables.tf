variable "location" {
  description = "Azure region for the test workload."
  type        = string
  default     = "Canada Central"
}

variable "prefix" {
  description = "Naming prefix used by the test resources."
  type        = string
  default     = "ccagenttest"
}
