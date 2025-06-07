# Instance Type Optimize Tools

An AWS Lambda-based tool that analyzes EC2 instance CPU utilization and provides optimization recommendations for cost efficiency and performance.

## Overview

This tool monitors EC2 instances across all AWS regions and analyzes their CPU utilization patterns over the past hour to provide intelligent scaling recommendations. It helps organizations optimize their AWS costs by identifying underutilized or overutilized instances.

## Features

- **Multi-Region Analysis**: Scans all available AWS regions for running EC2 instances
- **CPU Utilization Monitoring**: Uses CloudWatch metrics to analyze CPU usage patterns
- **Smart Recommendations**: 
  - Scale up for instances with >80% CPU utilization
  - Scale down for instances with <20% CPU utilization
  - Maintains current size for optimal instances
- **Tag-Based Exclusion**: Skip analysis for instances tagged with `CostNormExclude`
- **Error Handling**: Comprehensive error logging for troubleshooting
- **Cost Optimization**: Helps reduce AWS costs through right-sizing recommendations

## Architecture

- **Lambda Function**: Python-based serverless function for instance analysis
- **CloudWatch Integration**: Retrieves CPU utilization metrics
- **Terraform Deployment**: Infrastructure as Code for easy deployment
- **MCP Tool Integration**: Compatible with CostNorm's MCP tool framework

## Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform installed (v1.0+)
- Python 3.13 runtime support
- Required AWS permissions:
  - EC2 read permissions
  - CloudWatch read permissions
  - Lambda execution permissions

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Instance_Optimize_Tool
```

2. Configure AWS credentials:
```bash
aws configure --profile costnorm
```

3. Deploy infrastructure using Terraform:
```bash
cd IaC
terraform init
terraform plan
terraform apply
```

## Usage

The Lambda function accepts two main operations:

### 1. Get Instance Information
Analyzes all EC2 instances and returns optimization recommendations.

**Input:**
```json
{
  "body": {
    "tool_name": "get_instance_info"
  }
}
```

**Output:**
```json
{
  "optimizations_needed": [
    {
      "region": "us-east-1",
      "instance_id": "i-1234567890abcdef0",
      "instance_type": "t3.large",
      "metric": "CPUUtilization",
      "value": "85.2%",
      "recommendation": "scale_up"
    }
  ],
  "instances_ok": [...],
  "errors": [...]
}
```

### 2. Modify Instance Type
Simulates instance type modification (implementation pending for production use).

**Input:**
```json
{
  "body": {
    "tool_name": "modify_instance_type",
    "instance_id": "i-1234567890abcdef0",
    "new_type": "t3.xlarge"
  }
}
```

## Configuration

### Environment Variables
- **AWS_REGION**: Primary region for operations (default: us-east-1)
- **EXCLUDE_TAG_KEY**: Tag key for excluding instances (default: CostNormExclude)

### Lambda Configuration
- **Runtime**: Python 3.13
- **Architecture**: x86_64
- **Timeout**: 300 seconds
- **Memory**: 1024 MB

## Exclusion Tags

To exclude specific instances from analysis, add the `CostNormExclude` tag to your EC2 instances:

```bash
aws ec2 create-tags --resources i-1234567890abcdef0 --tags Key=CostNormExclude,Value=true
```

## Monitoring and Logging

The function provides comprehensive logging including:
- Instance analysis results
- CloudWatch metric retrieval errors
- Regional access issues
- Performance metrics

## Cost Considerations

- **Lambda Execution**: Charged per invocation and execution duration
- **CloudWatch API Calls**: Charged per API request
- **Cross-Region Data Transfer**: Minimal charges for multi-region analysis

## Security

- Uses AWS IAM roles for secure access
- No sensitive data stored in function code
- Supports AWS profile-based authentication
- Follows principle of least privilege

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue in the repository
- Contact the CostNorm team
- Check AWS documentation for service-specific troubleshooting

## Changelog

- **v1.0.0**: Initial release with multi-region EC2 analysis
- Support for CPU utilization monitoring
- Terraform-based deployment
- Tag-based exclusion system