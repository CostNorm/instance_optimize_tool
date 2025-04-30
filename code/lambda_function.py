import boto3
import json
from datetime import datetime, timedelta, timezone
from botocore.exceptions import ClientError

EXCLUDE_TAG_KEY = "CostNormExclude"

def get_instance_info():
    # Use default session credentials
    ec2_client = boto3.client('ec2', region_name='us-east-1')
    # Initialize result structure
    results = {
        "optimizations_needed": [],
        "instances_ok": [],
        "errors": []
    }
    regions = []
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(hours=1)

    # Get available regions
    try:
        regions_response = ec2_client.describe_regions()
        regions = [region['RegionName'] for region in regions_response.get('Regions', [])]
    except ClientError as e:
        results["errors"].append({"region": "global", "error_message": f"Error fetching AWS regions: {e}"})
        return results # Return early if regions cannot be fetched
    except Exception as e:
        results["errors"].append({"region": "global", "error_message": f"An unexpected error occurred while fetching regions: {e}"})
        return results

    if not regions:
        results["errors"].append({"region": "global", "error_message": "No accessible AWS regions found."})
        return results

    # Iterate through regions and fetch instance data
    for region in regions:
        try:
            regional_ec2_client = boto3.client('ec2', region_name=region)
            regional_cw_client = boto3.client('cloudwatch', region_name=region)
            paginator = regional_ec2_client.get_paginator('describe_instances')
            page_iterator = paginator.paginate(
                Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
            )

            for page in page_iterator:
                for reservation in page.get('Reservations', []):
                    for instance in reservation.get('Instances', []):
                        # 추가 시작: 제외 태그 확인
                        instance_tags = instance.get('Tags', [])
                        should_exclude = False
                        for tag in instance_tags:
                            if tag.get('Key') == EXCLUDE_TAG_KEY:
                                should_exclude = True
                                break
                        
                        if should_exclude:
                            instance_id_for_log = instance.get('InstanceId', 'N/A')
                            print(f"Excluding instance {instance_id_for_log} due to tag '{EXCLUDE_TAG_KEY}'.")
                            continue # 이 인스턴스 처리 건너뛰기
                        # 추가 끝

                        instance_id = instance.get('InstanceId', 'N/A')
                        instance_type = instance.get('InstanceType', 'N/A')
                        state = instance.get('State', {}).get('Name', 'N/A')
                        launch_time = instance.get('LaunchTime')
                        launch_time_str = launch_time.isoformat() if launch_time else 'N/A' # Use ISO format

                        cpu_avg = None
                        recommendation = None
                        cpu_usage_str = 'N/A' # For display if needed, not part of core data

                        try:
                            response = regional_cw_client.get_metric_statistics(
                                Namespace='AWS/EC2',
                                MetricName='CPUUtilization',
                                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                                StartTime=start_time,
                                EndTime=now,
                                Period=3600,
                                Statistics=['Average'],
                                Unit='Percent'
                            )
                            if response['Datapoints']:
                                cpu_avg = response['Datapoints'][0]['Average']
                                cpu_usage_str = f"{cpu_avg:.1f}%" # Keep for potential logging/debugging
                                
                                # Determine recommendation
                                if cpu_avg > 80.0:
                                    recommendation = "scale_up"
                                elif cpu_avg < 20.0:
                                    recommendation = "scale_down"
                                else:
                                    recommendation = "ok"
                            else:
                                recommendation = "pending_data"
                                
                        except ClientError as cw_error:
                            print(f"Could not get CloudWatch metrics for {instance_id} in {region}: {cw_error}")
                            recommendation = "error_fetching_cpu"
                            results["errors"].append({
                                "region": region,
                                "instance_id": instance_id,
                                "error_message": f"CloudWatch ClientError: {cw_error}"
                            })
                        except Exception as cw_e:
                            print(f"Unexpected error getting CloudWatch metrics for {instance_id} in {region}: {cw_e}")
                            recommendation = "error_fetching_cpu"
                            results["errors"].append({
                                "region": region,
                                "instance_id": instance_id,
                                "error_message": f"Unexpected CloudWatch Error: {cw_e}"
                            })

                        # Prepare instance data dictionary
                        instance_data = {
                            "region": region,
                            "instance_id": instance_id,
                            "instance_type": instance_type,
                            "metric": "CPUUtilization",
                            "value": f"{round(cpu_avg, 1)}%" if cpu_avg is not None else None,
                            # Include recommendation only if action is needed or ok
                            # recommendation field will be added when categorizing below
                        }
                        
                        # Categorize instance
                        if recommendation == "scale_up" or recommendation == "scale_down":
                             instance_data["recommendation"] = recommendation
                             results["optimizations_needed"].append(instance_data)
                        elif recommendation == "ok":
                             results["instances_ok"].append(instance_data)
                        # Instances with pending_data or error_fetching_cpu are implicitly not OK,
                        # and errors are logged in the errors list.

        except ClientError as e:
            print(f"Could not access region {region}: {e}") 
            results["errors"].append({"region": region, "error_message": f"EC2 ClientError: {e}"})
            continue
        except Exception as e:
            print(f"An unexpected error occurred in region {region}: {e}")
            results["errors"].append({"region": region, "error_message": f"Unexpected EC2 Error: {e}"})
            continue
    return results

def modify_instance_type(instance_id, new_type):
    # Simulate modifying instance type
    # In a real scenario, this would involve calling a cloud provider API (e.g., ec2.modify_instance_attribute)
    # **WARNING**: Directly calling modification APIs can have real cost and operational impact.
    print(f"Attempting to change instance {instance_id} to type {new_type}...")
    # Simulate success
    success = True 

    if success:
        return f"Successfully modified instance {instance_id} to type {new_type}."
    else:
        # In a real scenario, you might return specific error details
        return f"Failed to modify instance {instance_id}."


def lambda_handler(event, context):
    print(event)
    if event["body"]["tool_name"] == "get_instance_info":
        return get_instance_info()
    elif event["body"]["tool_name"] == "modify_instance_type":
        return modify_instance_type(event["body"]["instance_id"], event["body"]["new_type"])
    
    return {
        "statusCode": 403,
        "body": json.dumps({"message": "Invalid tool name"})
    }
