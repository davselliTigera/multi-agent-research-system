# Troubleshooting Guide

## Common Issues

### Image Pull Errors
**Symptom**: `ImagePullBackOff` or `ErrImagePull`

**Solution for Kind**:
```bash
kind load docker-image multi-agent-research/coordinator:latest
```

### Connection Timeouts
**Symptom**: "All connection attempts failed"

**Solution**:
```bash
./scripts/debug-connectivity.sh
```

### Pods Crash Looping
Check logs:
```bash
kubectl logs <pod-name>
kubectl describe pod <pod-name>
```

(To be expanded with more solutions)
