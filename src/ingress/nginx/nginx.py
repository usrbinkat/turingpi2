# nginx.py
import pulumi
import pulumi_kubernetes as k8s
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, FetchOpts
import re
import requests
from packaging import version

# Define the function to fetch the latest GitHub release version
def github_latest_release_version(gh_project):
    api_url = f"https://api.github.com/repos/{gh_project}/releases"
    response = requests.get(api_url)
    if response.status_code == 200:
        releases = response.json()
        helm_chart_releases = [release['tag_name'] for release in releases if release['tag_name'].startswith('helm-chart-')]
        if helm_chart_releases:
            # Sort releases by semantic versioning
            sorted_versions = sorted(helm_chart_releases, key=lambda v: version.parse(re.sub(r"[^0-9.]", "", v)), reverse=True)
            latest_helm_chart_release = sorted_versions[0]
            semver_version = re.sub(r"[^0-9.]", "", latest_helm_chart_release)
            return semver_version
        else:
            return "No helm-chart- releases found"
    else:
        return f"Failed to retrieve data: HTTP {response.status_code}"

def create_nginx_ingress(namespace_name, k8s_provider):

    # Retrieve Pulumi Config
    pulumi_config = pulumi.Config()

    # Evaluate the ingress-nginx version from the pulumi config.
    # If the version is not specified, fetch the latest version.
    ingress_nginx_version = pulumi_config.get("ingress-nginx.version")
    if not ingress_nginx_version:
        ingress_nginx_version = github_latest_release_version("kubernetes/ingress-nginx")

    namespace = k8s.core.v1.Namespace(
        f"{namespace_name}",
        metadata=k8s.meta.v1.ObjectMetaArgs(
            name=namespace_name,
            labels={
                "name": namespace_name,
                "environment": "dev",
                "layer": "platform"
            },
            annotations={
                "description": "Namespace for the Ingress Nginx Controller",
            }
        ),
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            protect=False
        )
    )

    # Deploy the NGINX Ingress Controller using a Helm Chart
    helm_chart = Chart(
        f"{namespace_name}",
        config=ChartOpts(
            chart='ingress-nginx',
            version=ingress_nginx_version,
            namespace=namespace_name,
            fetch_opts=FetchOpts(
                repo='https://kubernetes.github.io/ingress-nginx'
            ),
            values={
                'controller': {
                    'service': {
                        'type': 'LoadBalancer',
                        'externalTrafficPolicy': 'Local',
                    },
                },
            },
        ),
        opts=pulumi.ResourceOptions(
            provider=k8s_provider,
            depends_on=[namespace]
        )
    )

    pulumi.export("ingress_nginx_version", ingress_nginx_version)
    return namespace, helm_chart
