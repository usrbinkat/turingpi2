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

    try:
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
            ContainerPortArgs(name="code", container_port=7681)
        ]

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
            opts=pulumi.ResourceOptions(
                provider=k8s_provider
            )
        )

        service = k8s.core.v1.Service(
            'code',
            spec=k8s.core.v1.ServiceSpecArgs(
                selector={'app.kubernetes.io/name': 'konductor'},
                ports=[k8s.core.v1.ServicePortArgs(
                    name='code',
                    protocol='TCP',
                    port=7681,
                    target_port=7681
                )]
            ),
            opts=pulumi.ResourceOptions(
                provider=k8s_provider,
                depends_on=[deployment]
            )
        )

        ingress = k8s.networking.v1.Ingress(
            'konductor-code',
            metadata=k8s.meta.v1.ObjectMetaArgs(
                name='konductor-code',
                namespace='default',
                annotations={
                    'kubernetes.io/ingress.class': 'nginx',
                    'nginx.ingress.kubernetes.io/rewrite-target': '/'
                }
            ),
            spec=k8s.networking.v1.IngressSpecArgs(
                rules=[k8s.networking.v1.IngressRuleArgs(
                    http=k8s.networking.v1.HTTPIngressRuleValueArgs(
                        paths=[k8s.networking.v1.HTTPIngressPathArgs(
                            path='/code',
                            path_type='Prefix',
                            backend=k8s.networking.v1.IngressBackendArgs(
                                service=k8s.networking.v1.IngressServiceBackendArgs(
                                    name=service.metadata.name,
                                    port=k8s.networking.v1.ServiceBackendPortArgs(
                                        number=service.spec.ports[0].port
                                    )
                                )
                            )
                        )]
                    )
                )]
            ),
            opts=pulumi.ResourceOptions(
                provider=k8s_provider,
                depends_on=[service]
            )
        )

        return deployment, service, ingress

    except Exception as e:
        pulumi.log.error(f"Failed to create deployment: {e}")
        raise
