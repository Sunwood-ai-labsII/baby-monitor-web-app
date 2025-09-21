variable "project_id" {
  description = "The ID of the Google Cloud project where resources will be created."
  type        = string
}

variable "credentials_file" {
  description = "Optional path to a Google Cloud service account JSON key with sufficient permissions. Leave blank to use Application Default Credentials."
  type        = string
  default     = ""
}

variable "region" {
  description = "Google Cloud region to deploy networking resources in."
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "Google Cloud zone to deploy the compute instance in."
  type        = string
  default     = "us-central1-a"
}

variable "instance_name" {
  description = "Name of the Compute Engine instance."
  type        = string
  default     = "terraform-managed-vm"
}

variable "machine_type" {
  description = "Compute Engine machine type for the instance."
  type        = string
  default     = "e2-micro"
}

variable "boot_image" {
  description = "Source image used to initialize the VM's boot disk."
  type        = string
  default     = "debian-cloud/debian-12"
}

variable "boot_disk_size_gb" {
  description = "Size of the VM boot disk in GB."
  type        = number
  default     = 10
}

variable "boot_disk_type" {
  description = "Type of disk to use for the boot disk."
  type        = string
  default     = "pd-balanced"
}

variable "network_name" {
  description = "Name of the VPC network that will host the VM."
  type        = string
  default     = "terraform-vm-network"
}

variable "subnetwork_cidr" {
  description = "CIDR block for the custom subnetwork."
  type        = string
  default     = "10.0.0.0/24"
}

variable "ssh_source_ranges" {
  description = "List of CIDR blocks that are allowed to reach the VM over SSH."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "network_tag" {
  description = "Network tag applied to the VM for firewall targeting."
  type        = string
  default     = "terraform-vm"
}

variable "ssh_username" {
  description = "Linux username that will own the uploaded SSH public key."
  type        = string
}

variable "ssh_public_key" {
  description = "Public SSH key (in OpenSSH format) provided directly as a string."
  type        = string
  default     = ""
}

variable "ssh_public_key_file" {
  description = "Path to a file that contains the SSH public key. Takes precedence when ssh_public_key is empty."
  type        = string
  default     = ""
}

variable "ssh_private_key_file" {
  description = "Path to the private SSH key that pairs with the uploaded public key. Used to build a convenient ssh command output."
  type        = string
  default     = ""
}

variable "startup_script" {
  description = "Optional startup script executed the first time the instance boots."
  type        = string
  default     = ""
}

variable "startup_script_file" {
  description = "Path to a file with the startup script contents. Used when startup_script is not provided."
  type        = string
  default     = ""
}
