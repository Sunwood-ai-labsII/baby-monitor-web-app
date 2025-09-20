# Google Cloud VM Terraform Configuration

This Terraform configuration provisions a single Google Compute Engine VM along with the networking resources required for SSH access. The files are organised so you can quickly provide your own project details, credentials, and SSH key to bring the instance online.

## 📁 Repository Layout

- `main.tf` – Core infrastructure resources (network, firewall, static IP, Compute Engine instance).
- `variables.tf` – Input variables used to customise the deployment.
- `outputs.tf` – Helpful values such as the external IP address and an SSH command template.
- `terraform.tfvars.example` – Sample variable definitions; copy to `terraform.tfvars` and update with your environment-specific values.

## ✅ Prerequisites

1. **Terraform** v1.3.0 or later installed locally.
2. **Google Cloud project** with the Compute Engine API enabled.
3. **Service account** JSON key with permissions to manage Compute Engine, VPC networks, and firewall rules. Store the key securely and reference its path via the `credentials_file` variable.
4. **SSH key pair** (OpenSSH format). Supply the public key and the username that should own it on the VM.

## 🚀 Usage

1. Move into the Terraform directory in this repository:

   ```bash
   cd terraform
   ```

2. Copy the example variables file and customise the values:

   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your editor of choice
   ```

3. Initialise the Terraform working directory:

   ```bash
   terraform init
   ```

4. Review the planned infrastructure changes:

   ```bash
   terraform plan
   ```

5. Apply the configuration to create the resources:

   ```bash
   terraform apply
   ```

   Confirm the apply when prompted. Terraform will output the VM's public IP and a ready-to-use SSH command once provisioning completes.

6. SSH into the VM using the command displayed in the outputs:

   ```bash
   ssh <ssh_username>@<public_ip>
   ```

## 🔒 Security Notes

- Restrict `ssh_source_ranges` to trusted IP address ranges whenever possible instead of leaving it open to the internet.
- Rotate or revoke the service account key when it is no longer needed.
- If you provide a startup script, ensure it only performs actions you trust.

## 🧹 Clean-up

When you are finished testing, destroy the infrastructure to avoid ongoing charges:

```bash
terraform destroy
```

Confirm the destroy when prompted to remove all resources that were created.

