import pulumi
import pulumi_kubernetes as k8s
from pulumi_kubernetes.apps.v1 import Deployment, DeploymentSpecArgs
from pulumi_kubernetes.core.v1 import ContainerArgs, PodSpecArgs, PodTemplateSpecArgs
from pulumi_kubernetes.core.v1 import EnvVarArgs, VolumeArgs, VolumeMountArgs
from pulumi_kubernetes.meta.v1 import LabelSelectorArgs, ObjectMetaArgs
from pulumi_kubernetes.core.v1 import ContainerPortArgs

def create_konductor_deployment(name, image, replicas, k8s_provider):
    """
    Creates a Kubernetes deployment for the Konductor application.

    :param name: The name of the deployment.
    :param image: The Docker image to use for the deployment.
    :param replicas: The number of replicas to deploy.
    :param k8s_provider: The Pulumi Kubernetes provider.
    :return: The created Deployment object.
    """
    app_labels = {
        "app.kubernetes.io/name": "konductor",
        "app.kubernetes.io/managed": "pulumi",
    }
    env_args = [EnvVarArgs(name="TZ", value="UTC")]
    volumes = [VolumeArgs(name="tmp", empty_dir={})]
    volume_mounts = [VolumeMountArgs(name="tmp", mount_path="/tmp/tmp")]
    service_ports = [
        ContainerPortArgs(name="ssh", container_port=2222),
        ContainerPortArgs(name="http", container_port=8080),
        ContainerPortArgs(name="mosh", container_port=6000),
        ContainerPortArgs(name="hugo", container_port=1313),
        ContainerPortArgs(name="vscode", container_port=7681)
    ]

    try:
        deployment = Deployment(
            name,
            spec=DeploymentSpecArgs(
                selector=LabelSelectorArgs(match_labels=app_labels),
                replicas=replicas,
                template=PodTemplateSpecArgs(
                    metadata=ObjectMetaArgs(labels=app_labels),
                    spec=PodSpecArgs(
                        containers=[
                            ContainerArgs(
                                name=name,
                                image=image,
                                env=env_args,
                                ports=service_ports,
                                volume_mounts=volume_mounts
                            )
                        ],
                        volumes=volumes
                    ),
                ),
            ),
            opts=pulumi.ResourceOptions(provider=k8s_provider)
        )
        return deployment
    except Exception as e:
        pulumi.log.error(f"Failed to create deployment: {e}")
        raise
