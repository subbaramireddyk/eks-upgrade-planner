# EKS Upgrade Plan: production-cluster

**Generated:** 2024-01-15 10:30:00  
**Current Version:** 1.27  
**Target Version:** 1.29

## Executive Summary

- **Current EKS Version:** 1.27
- **Target EKS Version:** 1.29
- **Risk Level:** MEDIUM
- **Estimated Effort:** 5.5 hours
- **Recommended Downtime Window:** 1.5 - 2.0 hours
- **Version Jumps Required:** 2

## Current State

- **Cluster:** production-cluster (vpc-0abc123def456)
- **EKS Version:** 1.27
- **Platform Version:** eks.5
- **Status:** ACTIVE
- **Node Groups:** 3 groups (total 15 nodes)
- **Addons:** 5 installed
- **Region:** us-west-2

### Node Groups
| Name | Version | AMI Type | Capacity | Instance Types |
| --- | --- | --- | --- | --- |
| prod-ng-general | 1.27 | AL2_x86_64 | 5 | t3.large, t3.xlarge |
| prod-ng-compute | 1.27 | AL2_x86_64 | 8 | c5.2xlarge |
| prod-ng-memory | 1.27 | AL2_x86_64 | 2 | r5.2xlarge |

### Installed Addons
| Addon | Version | Status |
| --- | --- | --- |
| coredns | v1.9.3-eksbuild.2 | ACTIVE |
| kube-proxy | v1.27.1-eksbuild.1 | ACTIVE |
| vpc-cni | v1.12.6-eksbuild.1 | ACTIVE |
| aws-ebs-csi-driver | v1.19.0-eksbuild.2 | ACTIVE |
| aws-efs-csi-driver | v1.5.8-eksbuild.1 | ACTIVE |

## Upgrade Path

1. **Current:** EKS 1.27
2. ✅ Upgrade to EKS 1.28
3. ✅ Upgrade to EKS 1.29

⚠️  **Note:** Cannot skip minor versions - sequential upgrades required

## Pre-Upgrade Requirements

- [ ] Update coredns: v1.9.3-eksbuild.2 → v1.11.1-eksbuild.1
- [ ] Update kube-proxy: v1.27.1-eksbuild.1 → v1.29.3-eksbuild.1
- [ ] Update vpc-cni: v1.12.6-eksbuild.1 → v1.16.2-eksbuild.1
- [ ] Update aws-ebs-csi-driver: v1.19.0-eksbuild.2 → v1.27.0-eksbuild.1
- [ ] Fix 2 deprecated APIs in workloads
- [ ] Backup cluster configuration and data
- [ ] Test upgrade in staging environment
- [ ] Review breaking changes documentation
- [ ] Prepare rollback plan

## Deprecated APIs Found

⚠️  2 resources using deprecated APIs:

### networking.k8s.io/v1beta1 (removed in 1.22)
**Replacement:** networking.k8s.io/v1

- Ingress `app-ingress` in namespace `production`
- Ingress `api-ingress` in namespace `production`

## Breaking Changes

Found 3 breaking changes:

### [HIGH] PodSecurityPolicy removed (v1.25)
Pod Security Policy API has been removed. Use Pod Security Standards instead.
**Action Required:** Migrate to Pod Security Standards or third-party admission controllers

### [MEDIUM] HPA v2beta2 removed (v1.26)
HorizontalPodAutoscaler v2beta2 API has been removed
**Action Required:** Update to autoscaling/v2

### [MEDIUM] CSI migration (v1.27)
In-tree storage plugins being migrated to CSI
**Action Required:** Review storage configuration

## Migration Requirements

- **Manifest Updates Required:** 2 resources
- **Critical Migrations:** 2
- **Estimated Migration Time:** 0.3 hours

### Manual Interventions Required

- **[HIGH]** 2 resources need API version updates
  - Action: Update manifests and re-apply resources

- **[HIGH]** PodSecurityPolicy removed
  - Action: Implement Pod Security Standards

- **[MEDIUM]** Verify all CRDs are compatible
  - Action: Check CRD versions and update if needed

## Detailed Upgrade Steps

### Phase 1: Pre-Upgrade Preparation
**Estimated Duration:** 2-4 hours

1. Complete all checklist items
2. Backup cluster and workload data
3. Verify rollback plan
4. Communicate maintenance window

### Phase 2: Critical Addon Updates (Pre-EKS)
**Estimated Duration:** 30-60 minutes

1. Upgrade vpc-cni to compatible version
2. Upgrade kube-proxy to compatible version
3. Upgrade coredns to compatible version

### Phase 3: EKS Control Plane Upgrade to 1.28
**Estimated Duration:** 30-45 minutes

1. Update cluster version to 1.28
2. Wait for control plane to be active
3. Verify control plane health
4. Check API server logs

### Phase 4: EKS Control Plane Upgrade to 1.29
**Estimated Duration:** 30-45 minutes

1. Update cluster version to 1.29
2. Wait for control plane to be active
3. Verify control plane health
4. Check API server logs

### Phase 5: Node Group Updates
**Estimated Duration:** 1-2 hours

1. Update node group AMI to match control plane version
2. Perform rolling update of nodes
3. Monitor pod rescheduling
4. Verify all nodes are ready

### Phase 6: Additional Addon Updates (Post-EKS)
**Estimated Duration:** 20-30 minutes

1. Upgrade aws-ebs-csi-driver to recommended version
2. Upgrade aws-efs-csi-driver to recommended version

### Phase 7: Post-Upgrade Validation
**Estimated Duration:** 30-60 minutes

1. Verify cluster version
2. Check all nodes are ready
3. Verify all pods are running
4. Test critical workloads
5. Review cluster logs
6. Validate monitoring and alerts
7. Run smoke tests

## Risk Assessment

**Overall Risk Level:** MEDIUM

### Risk Factors

- ⚠️  2 resources using deprecated APIs
- ⚠️  3 breaking changes, 1 critical
- ⚠️  2 addons need updates
- ℹ️  2 sequential upgrades required

### Positive Factors

- ✅ Single version upgrade (per step)

### Mitigation Strategies

1. Update all deprecated API usage before upgrade
2. Review and test all breaking changes in staging
3. Upgrade incompatible addons before EKS upgrade
4. Plan for sequential upgrades with validation between

## Rollback Plan

In case of issues during upgrade:

### Immediate Rollback (Control Plane)
EKS control plane upgrades cannot be rolled back. However, you can:
1. Keep worker nodes on previous version temporarily
2. Restore from backup if data corruption occurs
3. Deploy new cluster from backup if necessary

### Node Group Rollback
1. Create new node group with previous AMI version
2. Drain pods from upgraded nodes
3. Delete upgraded node group
4. Verify all workloads are healthy

### Application Rollback
1. Revert any manifest changes using backups
2. Re-deploy previous application versions
3. Verify functionality

### Prevention
- Maintain comprehensive backups before upgrade
- Test rollback procedures in staging
- Document all changes made during upgrade

## Estimated Timeline

- **Pre Upgrade:** 120 minutes
- **Control Plane Upgrades:** 80 minutes (2 upgrades)
- **Node Rotations:** 135 minutes (3 groups)
- **Addon Upgrades:** 50 minutes (5 addons)
- **Validation:** 45 minutes

**Total Estimated Time:** 5.5 hours
**Recommended Maintenance Window:** 6-7 hours
