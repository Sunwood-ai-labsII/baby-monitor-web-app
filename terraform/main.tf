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

  credentials = var.credentials_file != "" ? file(var.credentials_file) : null
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
    "ssh-keys" = "${var.ssh_username}:${var.ssh_public_key}"
  }

  service_account {
    email  = data.google_compute_default_service_account.default.email
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }

  metadata_startup_script = var.startup_script != "" ? var.startup_script : null
}

