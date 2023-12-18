# TuringPi2

Turing Pi 2 Kubernetes Platform Engineering Lab.

## About

This is a Pulumi based Infrastructure as Code (IaC) project for developing a self serve Kubernetes Platform on the Turing Pi 2.

### Included:

* Pulumi Python IaC
* [Konductor DevOps Container](src/konductor/)

## Getting Started

1. Pulumi Login

```bash
pulumi login
```

2. Import Pulumi ESC (Environment, Secrets, Configuration)

```bash
eval (esc env --env usrbinkat/turingpi2 open --format shell)
```

3. Pulumi Stack

```bash
git clone https://github.com/usrbinkat/turingpi2
cd turingpi2
pulumi stack init
```

4. Pulumi Up

```bash
pulumi up -y --skip-preview
```