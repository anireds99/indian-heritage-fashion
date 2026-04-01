# FashionBrand Deployment Guide

## Deployment Options

### Option 1: Render.com (Recommended - Free Tier Available)

#### Prerequisites
- GitHub repository with the code
- Render.com account (https://render.com)

#### Steps to Deploy

1. **Push code to GitHub**
```bash
git add .
git commit -m "Ready for production deployment"
git push origin main
```

2. **Connect to Render.com**
   - Sign up at https://render.com
   - Create new Web Service
   - Connect your GitHub repository
   - Select the FashionBrand repository

3. **Configure Environment**
   - Set **Build Command:** `pip install -r requirements.txt`
   - Set **Start Command:** `gunicorn app:app`
   - Add **Environment Variables:**
     ```
     FLASK_ENV=production
     SECRET_KEY=your-secret-key-here (use `python -c 'import secrets; print(secrets.token_hex(32))'`)
     ```

4. **Database Setup**
   - Render will automatically create instance directory
   - Database will be created on first run
   - Default super admin: superadmin/Admin@123456

5. **Custom Domain (Optional)**
   - Point domain to Render's DNS
   - Add custom domain in Render dashboard

#### Render Deployment URL
- Default: `https://fashionbrand-[random].onrender.com`
- Custom: `https://www.rootsfashion.in` (if domain configured)

---

### Option 2: Heroku

#### Prerequisites
- Heroku CLI installed
- Heroku account

#### Steps
```bash
# Login to Heroku
heroku login

# Create app
heroku create fashionbrand

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

---

### Option 3: DigitalOcean App Platform

1. Connect GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set run command: `gunicorn app:app`
4. Configure environment variables
5. Deploy!

---

### Option 4: AWS (EC2 + RDS)

#### Prerequisites
- AWS Account
- EC2 instance running Ubuntu
- RDS PostgreSQL instance

#### Steps
1. SSH into EC2 instance
2. Clone repository
3. Install Python 3.9+
4. Create virtual environment
5. Install dependencies: `pip install -r requirements.txt`
6. Configure environment variables
7. Run with gunicorn: `gunicorn app:app --bind 0.0.0.0:5000`
8. Use Nginx as reverse proxy

---

## Environment Variables for Production

**Critical Settings:**
```bash
FLASK_ENV=production
SECRET_KEY=generate-with-python-secrets
DATABASE_URL=sqlite:///instance/fashion_brand.db  # or PostgreSQL URL
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
```

---

## Pre-Deployment Checklist

- [ ] All tests passing (`python test_application.py`)
- [ ] Endpoints tested (`python test_endpoints.py`)
- [ ] Secret key configured and strong
- [ ] Debug mode disabled (FLASK_ENV=production)
- [ ] Email configuration set (if sending emails)
- [ ] Database backup created
- [ ] Static files collected
- [ ] Requirements.txt updated
- [ ] Procfile configured
- [ ] .env file not committed to git
- [ ] README.md updated with deployment info

---

## Post-Deployment Verification

1. **Test Homepage**
   - Visit: `https://your-domain.com/`
   - Should see ROOTS homepage

2. **Test Authentication**
   - Visit: `https://your-domain.com/auth/login`
   - Try login with superadmin/Admin@123456

3. **Test Admin Dashboard**
   - Visit: `https://your-domain.com/admin/dashboard`
   - Should show statistics and recent orders

4. **Test Shop**
   - Visit: `https://your-domain.com/shop`
   - Should display 15 products

5. **Monitor Logs**
   - Check deployment provider's logs for errors
   - Set up error monitoring (Sentry recommended)

---

## Performance Optimization

### Database
- Use PostgreSQL for production (better than SQLite)
- Enable query caching
- Regular backups

### Caching
- Use Redis for session storage
- Cache static assets with CDN
- Browser caching headers configured

### Static Files
- Compress CSS/JS
- Use CDN for images
- Lazy load images

---

## Security Checklist

- [ ] HTTPS enabled
- [ ] Secret key strong and random
- [ ] Database credentials secured
- [ ] Email credentials secured
- [ ] CORS configured properly
- [ ] SQL injection prevention (SQLAlchemy ORM used)
- [ ] XSS protection enabled
- [ ] Rate limiting configured (optional)
- [ ] Admin panel protected
- [ ] Input validation on all forms

---

## Monitoring & Maintenance

### Logs
- Monitor application logs daily
- Set up email alerts for errors
- Archive old logs

### Database
- Backup daily
- Monitor disk usage
- Regular cleanup of old data

### Performance
- Monitor response times
- Track user traffic
- Optimize slow queries

### Updates
- Update dependencies monthly
- Security patches immediately
- Test updates in staging first

---

## Rollback Plan

If deployment fails:
1. Render: Switch to previous deployment
2. Heroku: `heroku rollback`
3. Manual: Redeploy previous version from git

---

## Support & Troubleshooting

### Common Issues

**404 on static files:**
- Check STATIC_FOLDER configuration
- Verify CSS/JS files exist in static/

**Database errors:**
- Check DATABASE_URL is correct
- Verify database file permissions
- Check disk space available

**Authentication failing:**
- Verify SECRET_KEY is set
- Check user credentials in database
- Review logs for errors

### Getting Help
- Check Flask documentation
- Review deployment provider's docs
- Check application logs
- Run diagnostic scripts

---

**Deployment Date:** March 31, 2026
**Status:** Ready for Production
**Last Updated:** Session 3
