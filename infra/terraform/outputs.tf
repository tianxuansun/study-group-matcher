output "alb_dns_name" {
  value = aws_lb.app.dns_name
}

output "db_endpoint" {
  value       = aws_db_instance.db.address
  description = "RDS endpoint hostname (port 5432)"
}

output "ecr_repository_url" {
  value       = aws_ecr_repository.repo.repository_url
  description = "ECR repo URL (tag your image and push, then set var.container_image)"
}
