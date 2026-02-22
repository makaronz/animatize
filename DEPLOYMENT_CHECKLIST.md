> [!WARNING]
> **DEPRECATED / OUTDATED**: This document may contain historical flows and commands that are not the canonical runtime path anymore.
> Use **README.md** for onboarding and runtime startup, **docs/API.md** for endpoints, **docs/ARCHITECTURE.md** for system flow, and **docs/OPERATIONS.md** for troubleshooting.

# 📋 Deployment Checklist

Use this checklist to ensure a smooth deployment of the ANIMAtiZE Framework.

## Pre-Deployment

### System Requirements
- [ ] Python 3.8+ installed (manual deployment)
- [ ] Docker 20.10+ installed (container deployment)
- [ ] Docker Compose 2.0+ installed (optional)
- [ ] kubectl installed (Kubernetes deployment)
- [ ] 4GB+ RAM available
- [ ] 10GB+ disk space available

### Configuration
- [ ] Clone repository
- [ ] Create `.env` file from `.env.example`
- [ ] Set `OPENAI_API_KEY` in `.env`
- [ ] Review and customize other environment variables
- [ ] Configure firewall rules (if applicable)
- [ ] Set up SSL/TLS certificates (production)

### Security
- [ ] API keys stored securely (not in code)
- [ ] `.env` file added to `.gitignore`
- [ ] Secrets management configured (production)
- [ ] Network security groups configured
- [ ] Rate limiting configured
- [ ] CORS origins properly set

## Deployment

### Docker Deployment
- [ ] Build Docker image: `docker build -t animatize:latest .`
- [ ] Test image locally: `docker run -p 8000:8000 animatize:latest`
- [ ] Verify health check: `curl http://localhost:8000/health`
- [ ] Push to registry (if using remote)
- [ ] Deploy to target environment

### Docker Compose Deployment
- [ ] Review `docker-compose.yml`
- [ ] Start services: `docker compose up -d`
- [ ] Verify all containers running: `docker compose ps`
- [ ] Check logs: `docker compose logs -f`
- [ ] Test health endpoint

### Kubernetes Deployment
- [ ] Update secrets in `k8s/deployment.yaml`
- [ ] Apply namespace: `kubectl apply -f k8s/deployment.yaml`
- [ ] Verify pods running: `kubectl get pods -n animatize`
- [ ] Check service status: `kubectl get svc -n animatize`
- [ ] Configure ingress (if needed)
- [ ] Set up auto-scaling
- [ ] Configure persistent volumes

### Manual Deployment
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Run health check script
- [ ] Configure systemd service (Linux)
- [ ] Start application
- [ ] Verify process running

## Post-Deployment

### Verification
- [ ] Health check passes: `curl http://localhost:8000/health`
- [ ] API responds: `curl http://localhost:8000/`
- [ ] Logs are being written
- [ ] Metrics are being collected
- [ ] No error messages in logs

### Monitoring
- [ ] Set up log aggregation
- [ ] Configure monitoring dashboards
- [ ] Set up alerts for errors
- [ ] Configure performance monitoring
- [ ] Set up uptime monitoring

### Testing
- [ ] Run integration tests
- [ ] Test API endpoints
- [ ] Verify image analysis works
- [ ] Test with sample images
- [ ] Load testing (production)

### Documentation
- [ ] Update deployment documentation
- [ ] Document any custom configurations
- [ ] Update runbooks
- [ ] Share access credentials securely
- [ ] Document backup procedures

## Rollback Plan

### If Deployment Fails
- [ ] Stop new deployment
- [ ] Check logs for errors
- [ ] Revert to previous version
- [ ] Notify team
- [ ] Document issues
- [ ] Create action items

### Docker Rollback
```bash
docker stop animatize
docker rm animatize
docker run -d --name animatize previous-image:tag
```

### Kubernetes Rollback
```bash
kubectl rollout undo deployment/animatize -n animatize
kubectl rollout status deployment/animatize -n animatize
```

## Production Checklist

### Before Going Live
- [ ] All pre-deployment checks complete
- [ ] Load testing completed
- [ ] Security audit completed
- [ ] Backup strategy implemented
- [ ] Disaster recovery plan documented
- [ ] Team trained on operations
- [ ] Support contacts documented
- [ ] Monitoring and alerts active

### Launch
- [ ] Deploy to production
- [ ] Verify health checks
- [ ] Monitor metrics closely
- [ ] Be available for support
- [ ] Monitor error rates
- [ ] Check performance metrics

### Post-Launch
- [ ] Monitor for 24 hours
- [ ] Review logs for issues
- [ ] Check performance metrics
- [ ] Gather user feedback
- [ ] Document lessons learned
- [ ] Plan improvements

## Maintenance

### Regular Tasks
- [ ] Check logs weekly
- [ ] Review metrics weekly
- [ ] Update dependencies monthly
- [ ] Security patches as needed
- [ ] Performance optimization quarterly
- [ ] Backup verification monthly

### Updates
- [ ] Test updates in staging first
- [ ] Create deployment plan
- [ ] Schedule maintenance window
- [ ] Notify users (if applicable)
- [ ] Deploy updates
- [ ] Verify success
- [ ] Monitor post-update

## Emergency Contacts

### Team
- DevOps Lead: [Name/Email]
- Backend Lead: [Name/Email]
- Security Lead: [Name/Email]
- On-Call: [Phone/Pager]

### External
- Cloud Provider Support: [Contact]
- API Provider Support: [Contact]
- Monitoring Service: [Contact]

## Notes

- Use this checklist for each deployment
- Update as processes evolve
- Keep track of issues encountered
- Share learnings with team

---

**Last Updated**: 2026-02-08  
**Version**: 1.0  
**Owner**: DevOps Team
