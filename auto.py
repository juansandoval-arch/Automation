import os
import boto3
import requests
import numpy as np
import time

def get_cpu_utilization(service_name, cluster_name, minutes=30):
    api_key = os.getenv('DATADOG_API_KEY')
    app_key = os.getenv('DATADOG_APP_KEY')

    if not api_key or not app_key:
        raise ValueError("Faltan variables de entorno de Datadog.")

    end_time = int(time.time())
    start_time = end_time - (minutes * 60)

    url = "https://api.datadoghq.com/api/v1/query"

    query = f"avg:ecs.fargate.cpu.percent{{task_family:{service_name}}}"

    params = {
        'from': start_time,
        'to': end_time,
        'query': query
    }

    headers = {
        "DD-API-KEY": api_key,
        "DD-APPLICATION-KEY": app_key
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()

    values = [
        point[1]
        for series in data.get('series', [])
        for point in series.get('pointlist', [])
        if point[1] is not None
    ]

    return values


def analyze_cpu(cpu_values):
    if not cpu_values:
        return None, None, "No data"

    avg_cpu = np.mean(cpu_values)
    max_cpu = np.max(cpu_values)

    trend_value = np.mean(np.diff(cpu_values)) if len(cpu_values) > 1 else 0

    if trend_value > 0.5:
        trend = "Increasing"
    elif trend_value < -0.5:
        trend = "Decreasing"
    else:
        trend = "Stable"

    return avg_cpu, max_cpu, trend


def main():
    service_name = "sup-da-pulsar-consumer-sn"
    cluster_name = "prod-da-backend"

    try:
        cpu_values = get_cpu_utilization(service_name, cluster_name)

        avg_cpu, max_cpu, trend = analyze_cpu(cpu_values)

        if avg_cpu is None:
            print("No se encontraron métricas.")
            return

        if avg_cpu > 85 and trend == "Increasing":
            recommendation = "🚨 Alto riesgo - Escalar a N2"
        elif avg_cpu > 80:
            recommendation = "⚠️ Warning - Monitorear"
        else:
            recommendation = "✅ Normal"

        print(f"""
🧠 N1 AUTO-ANALYSIS

Service: {service_name}
Cluster: {cluster_name}

Avg CPU: {avg_cpu:.2f}%
Max CPU: {max_cpu:.2f}%
Trend: {trend}

Recommendation:
{recommendation}
""")

    except Exception as e:
        print("Error:", str(e))


if __name__ == "__main__":
    main()