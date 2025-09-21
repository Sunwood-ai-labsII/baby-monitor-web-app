output "instance_name" {
  description = "Name of the created Compute Engine instance."
  value       = google_compute_instance.vm.name
}

output "instance_public_ip" {
  description = "Static external IP address reserved for the instance."
  value       = google_compute_address.vm_ip.address
}

output "ssh_command" {
  description = "Convenience SSH command that includes the private key flag when provided."
  value       = var.ssh_private_key_file != "" ? "ssh -i ${pathexpand(var.ssh_private_key_file)} ${var.ssh_username}@${google_compute_address.vm_ip.address}" : "ssh ${var.ssh_username}@${google_compute_address.vm_ip.address}"
}
