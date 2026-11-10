variable "region" { default = "us-east-1" }
variable "availability_zone" { type = string }
variable "firewall_ami_id" {
  type        = string
  description = "Exact subscribed Marketplace VM-Series AMI for this region; no guessed AMI."
  validation {
    condition     = can(regex("^ami-[0-9a-f]+$", var.firewall_ami_id))
    error_message = "Supply the regional Marketplace AMI ID."
  }
}
variable "firewall_instance_type" {
  type        = string
  description = "Supported x86 instance type from the selected offer; must support three ENIs."
}
variable "admin_cidr" {
  type = string
  validation {
    condition     = can(cidrhost(var.admin_cidr, 0)) && can(regex("/32$", var.admin_cidr))
    error_message = "Use your single public IPv4 address with /32."
  }
}
variable "ssh_public_key" {
  type        = string
  description = "Public key only. Keep the private key on your machine."
}
