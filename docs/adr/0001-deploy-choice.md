# ADR-0001 — ECS Fargate + RDS for Study Group Matcher

**Status**: Accepted  
**Date**: 2025-11-02

## Context
We need a low-ops, scalable way to deploy a small FastAPI service with a relational DB, clear health endpoints, metrics, and alarms. Team uses Docker already; infra should integrate with CloudWatch and CI/CD easily.

## Options considered
- **EC2 + Systemd**: Flexible but higher ops load (patching, AMIs, scaling).
- **EKS (Kubernetes)**: Powerful but overkill for single service; higher cognitive/ops overhead.
- **ECS on Fargate**: Serverless containers, native ALB/CloudWatch integration, simplest path to prod for Dockerized APIs.

## Decision
Choose **ECS Fargate** with an **ALB** and **RDS Postgres**. Emit app metrics using **AWS Embedded Metric Format** and set alarms on ALB 5xx and p95 latency.

## Consequences
- + Simple deploys via GitHub Actions to ECR + ECS
- + CloudWatch-native log/metric/alarms
- - Less portable than generic k8s
- - Vendor-specific metrics format (EMF), acceptable for AWS footprint
