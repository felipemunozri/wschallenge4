# Whitestack challenge 4

El challenge consistió en implementar las herramientas **Prometheus Operator** junto a **Prometheus Adapter** y un **HPA** (Horizontal Pod Autoscaler) para lograr escalar una aplicación de acuerdo a un incremento del tráfico.

## Modificar la aplicación base y usar librería prometheus_client

- Añadimos la librería **prometheus_client** en el fichero **requirements.txt**.

- Definimos un **Counter** para contabilizar la cantidad de consultas recibidas en la ruta **/heavywork** y agregamos la ruta **/metrics** para exponer las métricas en formato de Prometheus.

- Ejecutamos la aplicación y comprobamos que efectivamente se estén contabilizando las solicitudes a la ruta **/heavywork**:

![local_heavywork](/img/local_heavywork.png)

## Desplegar app en Kubernetes

- Crear **Kind** cluster con capacidad para ingress:

```shell
kind create cluster --config ./kind/config.yaml -n wschallenge4

kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
```

- Crear namespaces, desplegar app, desplegar ingress:

```shell
kubectl apply -f ./k8s/base/.
```

- Verificar funcionamiento de app y métricas:

![ingress_heavywork](/img/ingress_heavywork.png)

## Crear ServiceMonitor

- Instalar **kube-prometheus-stack** que incluye la herramienta **Prometheus Operator**:

```shell
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack -n monitoring
```

- Desplegar **ServiceMonitor**:

```shell
kubectl apply -f ./k8s/service-monitor.yaml -n python-app
```

- Verificar el funcionamiento de la métrica en Prometheus:

![prometheus_heavywork](/img/prometheus_heavywork.png)

## Crear Prometheus Adapter y HPA

- Instalar **Prometheus Adapter** usando loa valores en el fichero **prometheus-adapter-values.yaml**. En este caso la métrica externa se declaro dentro del mismo fichero de customización del chart en lugar de cargarlo como un ConfigMap:

```shell
helm upgrade --install prometheus-adapter prometheus-community/prometheus-adapter \
  -f ./k8s/prometheus-adapter-values.yaml \
  -n monitoring
```

- Verificar que aparezca la external rule en la api external.metrics.k8s.io/v1beta1:

```shell
kubectl get --raw "/apis/external.metrics.k8s.io/v1beta1" | jq . | grep "heavywork_requests_per_second"
```

- Desplegar el **HPA** y verificar la configuración:

```shell
kubectl apply -f ./k8s/python-app-hpa.yaml -n python-app
```

![hpa](/img/hpa.png)

- Ejecutar el script **generate_load.py** para verficar el scale up de la aplicación (se aumentó el valor de **arrival_rate** de 20 a 200):

![hpa_scaleup](/img/hpa_scaleup.png)

- Realizar request a la ruta **/lightwork** y verificar scale down de la aplicación:

![hpa_scaledown](/img/hpa_scaledown.png)
