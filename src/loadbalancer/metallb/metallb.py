# metallb.py
import pulumi
import pulumi_kubernetes as k8s
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts

def create_metallb(namespace_name, metallb_version, address_pool, k8s_provider):
    # Create a Kubernetes Namespace for MetalLB with security labels for the metallb speaker
    namespace = k8s.core.v1.Namespace(
        namespace_name,
        metadata=k8s.meta.v1.ObjectMetaArgs(
            name=namespace_name,
            labels={
                "name": namespace_name,
                "environment": "dev",
                "layer": "platform",
                "pod-security.kubernetes.io/enforce": "privileged",
                "pod-security.kubernetes.io/audit": "privileged",
                "pod-security.kubernetes.io/warn": "privileged"
            }
        ),
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            protect=False
        )
    )

    helm_chart = Chart(
        f"{namespace_name}",
        config=ChartOpts(
            chart='metallb',
            version=metallb_version,
            namespace=namespace_name,
            skip_crd_rendering=False,
            fetch_opts=FetchOpts(
                repo='https://metallb.github.io/metallb'
            ),
            values={
                'crds': {
                    'enabled': True
                },
                'controller': {
                    'tolerations': [
                        {
                            'key': 'node-role.kubernetes.io/master',
                            'effect': 'NoSchedule'
                        }
                    ]
                },
                'speaker': {
                    'tolerations': [
                        {
                            'key': 'node-role.kubernetes.io/master',
                            'effect': 'NoSchedule'
                        }
                    ]
                }
            }
        ),
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            depends_on=[namespace]
        )
    )

    # Define the CustomResource for an IPAddressPool
    default_address_pool = k8s.apiextensions.CustomResource(
        resource_name="default-metallb-address-pool",
        api_version="metallb.io/v1beta1",
        kind="IPAddressPool",
        metadata=k8s.meta.v1.ObjectMetaArgs(
            name="default-metallb-address-pool",
            namespace=namespace_name,
        ),
        spec={
            "addresses": address_pool,
            "avoidBuggyIPs": True,
        },
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            depends_on=[helm_chart]
        )
    )

    # Export the name of the IPAddressPool
    pulumi.export('metallb_default_ip_address_pool', default_address_pool.spec['addresses'])

    # Return all resources
    return namespace, helm_chart, default_address_pool
