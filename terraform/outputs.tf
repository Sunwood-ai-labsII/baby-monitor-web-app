output "instance_name" {
  description = "Name of the created Compute Engine instance."
  value       = google_compute_instance.vm.name
}

output "instance_public_ip" {
  description = "Ephemeral public IP address assigned to the instance."
  value       = google_compute_address.vm_ip.address
}

output "ssh_command" {
  description = "Convenience SSH command that can be used once the instance is provisioned."
  value       = "ssh ${var.ssh_username}@${google_compute_address.vm_ip.address}"
}
