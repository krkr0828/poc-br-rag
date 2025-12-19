/**
 * Bedrock Resources
 *
 * Note: Knowledge Base and Guardrails must be created manually in AWS Console
 * This file uses data sources to reference existing resources
 *
 * See SETUP.md for manual setup instructions
 */

# ==============================================================================
# Knowledge Base (Reference to manually created resource)
# ==============================================================================

# Data source for Knowledge Base (after manual creation)
# Uncomment after creating the Knowledge Base in AWS Console
# data "aws_bedrockagent_knowledge_base" "main" {
#   knowledge_base_id = var.knowledge_base_id
# }

# ==============================================================================
# Guardrails (Reference to manually created resource)
# ==============================================================================

# Data source for Guardrails (after manual creation)
# Uncomment after creating Guardrails in AWS Console
# data "aws_bedrock_guardrail" "main" {
#   guardrail_identifier = var.guardrails_id
# }

# ==============================================================================
# Outputs for manual verification
# ==============================================================================

output "bedrock_model_id" {
  description = "Bedrock model ID to use"
  value       = "anthropic.claude-3-haiku-20240307-v1:0"
}

output "bedrock_setup_instructions" {
  description = "Instructions for Bedrock setup"
  value       = "See SETUP.md for Knowledge Base and Guardrails configuration"
}

# Placeholder outputs (update after manual creation)
output "knowledge_base_id_placeholder" {
  description = "Knowledge Base ID (set via terraform.tfvars after manual creation)"
  value       = var.knowledge_base_id != "" ? var.knowledge_base_id : "NOT_SET - See SETUP.md"
}

output "guardrails_id_placeholder" {
  description = "Guardrails ID (set via terraform.tfvars after manual creation)"
  value       = var.guardrails_id != "" ? var.guardrails_id : "NOT_SET - See SETUP.md"
}
