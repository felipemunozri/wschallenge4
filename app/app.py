import os
from bottle import Bottle, request, response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Bottle()

# Crear un contador para /heavywork
heavywork_counter = Counter(
    'heavywork_requests_total', 'Total number of requests to /heavywork')


@app.get('/metrics')
def metrics():
    # Generar la información de las métricas
    response.content_type = CONTENT_TYPE_LATEST
    metrics_data = generate_latest()
    return metrics_data


@app.post('/heavywork')
def heavywork():
    # Incrementar el contador cada vez que se llama a /heavywork
    heavywork_counter.inc()
    response.status = 202
    return {"message": "Heavy work started"}


@app.post('/lightwork')
def lightwork():
    return {"message": "Light work done"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
