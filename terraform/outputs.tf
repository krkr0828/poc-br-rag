# Outputs will be populated as resources are created

output "project_info" {
  description = "Project information"
  value = {
    project_name = var.project_name
    environment  = var.environment
    region       = var.aws_region
  }
}
