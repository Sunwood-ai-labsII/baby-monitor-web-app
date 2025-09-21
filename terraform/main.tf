terraform {
  required_version = ">= 1.3.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone

  credentials = var.credentials_file != "" ? file(pathexpand(var.credentials_file)) : null
}

locals {
  ssh_public_key_from_var      = trimspace(var.ssh_public_key)
  ssh_public_key_file_expanded = var.ssh_public_key_file != "" ? pathexpand(var.ssh_public_key_file) : ""
  ssh_public_key_from_file     = local.ssh_public_key_file_expanded != "" ? trimspace(file(local.ssh_public_key_file_expanded)) : ""
  ssh_public_key_effective     = local.ssh_public_key_from_var != "" ? local.ssh_public_key_from_var : local.ssh_public_key_from_file

  startup_script_from_var_trimmed = trimspace(var.startup_script)
  startup_script_file_expanded    = var.startup_script_file != "" ? pathexpand(var.startup_script_file) : ""
  startup_script_from_file        = local.startup_script_file_expanded != "" ? file(local.startup_script_file_expanded) : ""
  startup_script_effective        = local.startup_script_from_var_trimmed != "" ? var.startup_script : (local.startup_script_file_expanded != "" && trimspace(local.startup_script_from_file) != "" ? local.startup_script_from_file : "")
}
data "google_compute_default_service_account" "default" {
  project = var.project_id
}

resource "google_compute_network" "vm_network" {
  name                    = var.network_name
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "vm_subnetwork" {
  name          = "${var.network_name}-subnet"
  ip_cidr_range = var.subnetwork_cidr
  region        = var.region
  network       = google_compute_network.vm_network.id
}

resource "google_compute_firewall" "ssh" {
  name    = "${var.network_name}-allow-ssh"
  network = google_compute_network.vm_network.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  direction     = "INGRESS"
  priority      = 1000
  source_ranges = var.ssh_source_ranges
  target_tags   = [var.network_tag]
}

resource "google_compute_address" "vm_ip" {
  name   = "${var.instance_name}-ip"
  region = var.region
}

resource "google_compute_instance" "vm" {
  name         = var.instance_name
  machine_type = var.machine_type
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = var.boot_image
      size  = var.boot_disk_size_gb
      type  = var.boot_disk_type
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.vm_subnetwork.id

    access_config {
      nat_ip = google_compute_address.vm_ip.address
    }
  }

  tags = [var.network_tag]

  metadata = {
    "ssh-keys" = "${var.ssh_username}:${local.ssh_public_key_effective}"
  }

  service_account {
    email  = data.google_compute_default_service_account.default.email
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }

  metadata_startup_script = local.startup_script_effective != "" ? local.startup_script_effective : null

  lifecycle {
    precondition {
      condition     = local.ssh_public_key_effective != ""
      error_message = "Either ssh_public_key or ssh_public_key_file must be provided and non-empty."
    }
  }
}

