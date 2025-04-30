module "mcp_tool_iac_template" {
  source = "github.com/CostNorm/mcp_tool_iac_template"
  function_name = "instance_optimize_tool"
  lambda_handler = "lambda_function.lambda_handler"
  lambda_runtime = "python3.13"
  lambda_architecture = "x86_64"
  lambda_timeout = 300
  lambda_memory = 1024
  attach_ec2_policy = true
  region = "us-east-1"
  profile = "costnorm"
}

