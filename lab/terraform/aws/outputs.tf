output "firewall_management_ip" { value = aws_eip.firewall.public_ip }
output "client_public_ip" { value = aws_instance.client.public_ip }
output "app_private_ip" { value = aws_instance.app.private_ip }
