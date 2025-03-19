import boto3
import json
from botocore.exceptions import BotoCoreError, ClientError

def get_pricing(service_code, region='Asia Pacific (Mumbai)'):
    try:
        # Initialize a session using Amazon Pricing
        pricing_client = boto3.client('pricing', region_name='us-east-1')

        # Retrieve pricing information for the specified service and region
        response = pricing_client.get_products(
            ServiceCode=service_code,
            Filters=[
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': region},
            ]
        )

        # Parse and return pricing information
        pricing_info = []
        for price_item in response['PriceList']:
            product = json.loads(price_item)
            attributes = product['product']['attributes']
            sku = product['product']['sku']
            instance_type = attributes.get('instanceType', 'N/A')
            location = attributes.get('location', 'N/A')
            storage_class = attributes.get('storageClass', 'N/A')
            price_dimensions = list(product['terms']['OnDemand'].values())[0]['priceDimensions']
            price_per_unit = list(price_dimensions.values())[0]['pricePerUnit'].get('USD', 'N/A')

            # Convert price per unit to price per hour if applicable
            if price_per_unit != 'N/A':
                if service_code == 'AmazonS3':
                    price_per_hour = float(price_per_unit) / (30 * 24)
                else:
                    price_per_hour = float(price_per_unit)
                price_per_hour = f"{price_per_hour:.8f}"
            else:
                price_per_hour = 'N/A'

            pricing_info.append({
                'Service': service_code,
                'SKU': sku,
                'Instance Type': instance_type,
                'Storage Class': storage_class,
                'Region': location,
                'Price per Unit (USD)': price_per_unit,
                'Price per Hour (USD)': price_per_hour
            })

        return pricing_info

    except (BotoCoreError, ClientError) as error:
        print(f"An error occurred: {error}")
        return []

def calculate_total_cost(json_file_path):
    with open(json_file_path, 'r') as file:
        architecture = json.load(file)

    total_hourly_cost = 0.0
    total_monthly_cost = 0.0
    service_details = []

    for node in architecture['nodes']:
        service_type = node['type']
        pricing_info = get_pricing(service_type)
        if pricing_info:
            price_per_hour = pricing_info[0]['Price per Hour (USD)']
            if price_per_hour != 'N/A':
                hourly_cost = float(price_per_hour)
                monthly_cost = hourly_cost * 24 * 30  # Assuming 24/7 usage for a month
                total_hourly_cost += hourly_cost
                total_monthly_cost += monthly_cost
                service_details.append({
                    'Service': service_type,
                    'Instance Type': pricing_info[0]['Instance Type'],
                    'Region': pricing_info[0]['Region'],
                    'Hourly Cost (USD)': f"{hourly_cost:.8f}",
                    'Monthly Cost (USD)': f"{monthly_cost:.2f}"
                })

    for detail in service_details:
        print(f"Service: {detail['Service']}")
        print(f"Instance Type: {detail['Instance Type']}")
        print(f"Region: {detail['Region']}")
        print(f"Hourly Cost (USD): ${detail['Hourly Cost (USD)']}")
        print(f"Monthly Cost (USD): ${detail['Monthly Cost (USD)']}")
        print("-" * 40)

    print(f"Total Hourly Cost: ${total_hourly_cost:.8f}")
    print(f"Total Monthly Cost: ${total_monthly_cost:.2f}")

if __name__ == "__main__":
    calculate_total_cost('demo.json')