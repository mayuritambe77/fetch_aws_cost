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

        # Parse and display pricing information
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

            print(f"Service: {service_code}")
            print(f"SKU: {sku}")
            print(f"Instance Type: {instance_type}")
            print(f"Storage Class: {storage_class}")
            print(f"Region: {location}")
            print(f"Price per Unit (USD): ${price_per_unit}")
            print(f"Price per Hour (USD): ${price_per_hour}")
            print("-" * 40)

    except (BotoCoreError, ClientError) as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    print("Fetching AWS Pricing Data... Please wait.\n")
    get_pricing('AmazonEC2')
