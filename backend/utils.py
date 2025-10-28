import pandas as pd
import boto3
from botocore.exceptions import ClientError
import os
import math

EXCEL_PATH = "../backend/RVTools_export_all_2025COPY.xlsx"

aws_ce = boto3.client("ce", region_name="us-east-1")  # Cost Explorer
aws_pricing = boto3.client("pricing", region_name="us-east-1")  # On-demand prices

def serializar(val):
    if isinstance(val, float) and math.isnan(val):
        return None
    return val

def buscar_servidor(vm_name):
    df = pd.read_excel(EXCEL_PATH)
    row = df[df["VM"] == vm_name]

    if row.empty:
        return None

    server = row.iloc[0].to_dict()
    server = {k: serializar(v) for k, v in server.items()}
    return server

def obtener_precio_catalogo(instance_type: str) -> float:
    try:
        response = aws_pricing.get_products(
            ServiceCode="AmazonEC2",
            Filters=[
                {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_type},
                {"Type": "TERM_MATCH", "Field": "location", "Value": "US East (N. Virginia)"},
                {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": "Linux"},
                {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
                {"Type": "TERM_MATCH", "Field": "capacitystatus", "Value": "Used"}
            ],
            MaxResults=1
        )

        price_item = response["PriceList"][0]
        import json
        price_item = json.loads(price_item)

        terms = price_item["terms"]["OnDemand"]
        term_key = list(terms.keys())[0]
        price_dimensions = terms[term_key]["priceDimensions"]
        dim_key = list(price_dimensions.keys())[0]
        price_per_hour = float(price_dimensions[dim_key]["pricePerUnit"]["USD"])

        return round(price_per_hour * 730, 2) # mensual aprox
    except Exception:
        return 0.0

def calcular_costo_aws(server_data: dict):
    instance_type = server_data.get("VM Config File", "t3.medium")  # Ajusta según tu Excel

    # Intentar obtener uso real en Cost Explorer
    try:
        response = aws_ce.get_cost_and_usage(
            TimePeriod={
                "Start": "2025-10-01",
                "End": "2025-10-31"
            },
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "RESOURCE_ID"}]
        )

        costo_real = 0.0
        for group in response["ResultsByTime"]:
            for item in group.get("Groups", []):
                if server_data["VM"] in item["Keys"][0]:
                    costo_real += float(item["Metrics"]["UnblendedCost"]["Amount"])

        if costo_real > 0:
            return {"total": round(costo_real, 2), "tipo": instance_type, "fuente": "Cost Explorer"}
    except ClientError:
        pass

    # Si no hay costo real → usar catálogo de precios EC2
    costo_estimado = obtener_precio_catalogo(instance_type)

    return {
        "total": costo_estimado,
        "tipo": instance_type,
        "fuente": "Pricing API"
    }
