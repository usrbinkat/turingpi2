import pulumi
import pulumi_kubernetes as k8s
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts
from src.konductor.pod import create_konductor_deployment
from src.lib.github import github_latest_release_version
from src.ingress.nginx.nginx import create_nginx_ingress
from src.loadbalancer.metallb.metallb import create_metallb

# Configuration for the Kubernetes provider
esc = "turingpi2"
pulumi_config = pulumi.Config()
kubeconfig = pulumi.Config(esc).get_secret("kubeconfig")
k8s_provider = k8s.Provider('kubeconfig', kubeconfig=kubeconfig)

# Evaluate the metallb version from the pulumi config.
# If the version is not specified, fetch the latest version.
helm_release_version = pulumi_config.get("metallb.version")
if not helm_release_version:
    helm_release_version = github_latest_release_version("metallb/metallb")

# Install MetalLB using a Helm Chart.
address_pool=["192.168.1.61-192.168.1.69"]
metallb = create_metallb(
    "metallb-system",
    helm_release_version,
    address_pool,
    k8s_provider
)

## Install the NGINX Ingress Controller using a Helm Chart.
#ingress_nginx = create_nginx_ingress(
#    "ingress-nginx",
#    k8s_provider
#)
#
## Create the Konductor DevOps Container deployment
#replica_count = 1
#name = "konductor"
#image = "ghcr.io/containercraft/konductor:latest"
#konductor_deployment = create_konductor_deployment(
#    name=name,
#    image=image,
#    replicas=replica_count,
#    k8s_provider=k8s_provider
#)
#
## Export deployment details
#pulumi.export("konductor_deployment", konductor_deployment.name)
