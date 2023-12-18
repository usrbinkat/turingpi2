import pulumi
import pulumi_kubernetes as k8s
from src.konductor.pod import create_konductor_deployment

# Configuration for the Kubernetes provider
kubeconfig = pulumi.Config("zephyr/usrbinkat-k8s").get_secret("microk8s.kubeconfig")
k8s_provider = k8s.Provider('k8s-provider', kubeconfig=kubeconfig)

# Parameters for the Konductor deployment
deployment_name = "konductor"
image_name = "ghcr.io/containercraft/konductor:latest"
replica_count = 1

# Create the Konductor deployment
konductor_deployment = create_konductor_deployment(
    name=deployment_name,
    image=image_name,
    replicas=replica_count,
    k8s_provider=k8s_provider
)

# Export deployment details
pulumi.export("deployment_name", konductor_deployment.metadata["name"])
pulumi.export("labels", konductor_deployment.spec.apply(lambda spec: spec.template.metadata.labels))
pulumi.export("replicas", konductor_deployment.spec.apply(lambda spec: spec.replicas))
