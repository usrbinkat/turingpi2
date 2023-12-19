import pulumi
import pulumi_kubernetes as k8s
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts
from src.konductor.pod import create_konductor_deployment

# Configuration for the Kubernetes provider
esc = "turingpi2"
kubeconfig = pulumi.Config(esc).get_secret("kubeconfig")
k8s_provider = k8s.Provider('microk8s-provider', kubeconfig=kubeconfig)

# Create the Konductor deployment
replica_count = 1
deployment_name = "konductor"
image_name = "ghcr.io/containercraft/konductor:latest"
konductor_deployment = create_konductor_deployment(
    name=deployment_name,
    image=image_name,
    replicas=replica_count,
    k8s_provider=k8s_provider
)

# Create a Kubernetes Namespace named 'ingress-nginx'
nginx_namespace = k8s.core.v1.Namespace("ingress-nginx",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="ingress-nginx",
    )
)

# Install the NGINX Ingress Controller using a Helm Chart.
nginx_ingress = Chart(
    'nginx-ingress',
    config=ChartOpts(
        chart='ingress-nginx',
        version='4.0.6',
        namespace=nginx_namespace.metadata.name,
        fetch_opts=FetchOpts(
            repo='https://kubernetes.github.io/ingress-nginx'
        ),
        values={
            'controller': {
                'service': {
                    'type': 'NodePort',
                    'nodePorts': {
                        'http': 30080,
                        'https': 30443,
                    },
                    'externalTrafficPolicy': 'Local',
                },
            },
        },
    ),
    opts=pulumi.ResourceOptions(
        provider=k8s_provider,
        depends_on=[
            nginx_namespace
        ]
    )
)

# Export deployment details
pulumi.export("deployment_name", konductor_deployment.metadata["name"])
pulumi.export("labels", konductor_deployment.spec.apply(lambda spec: spec.template.metadata.labels))
pulumi.export("replicas", konductor_deployment.spec.apply(lambda spec: spec.replicas))
