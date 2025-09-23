# 🚀 Deployment Guide - Streamlit Cloud

This guide will help you deploy your Coding Interview Revision System to Streamlit Cloud for mobile access.

## 📋 Prerequisites

1. **GitHub Account**: You'll need a GitHub account
2. **Git Repository**: Your code should be in a GitHub repository
3. **Streamlit Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)

## 🔧 Step-by-Step Deployment

### 1. Prepare Your Repository

Make sure your GitHub repository has these files:
```
├── web_app.py          # Main Streamlit app
├── core.py            # Core functionality
├── problem_bank.yaml  # Problem database
├── requirements.txt   # Dependencies
├── .streamlit/
│   └── config.toml    # Streamlit configuration
└── README.md          # Documentation
```

### 2. Push to GitHub

If you haven't already, push your code to GitHub:

```bash
git init
git add .
git commit -m "Initial commit - Coding Interview Revision System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

### 3. Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Fill in the details:
   - **Repository**: `YOUR_USERNAME/YOUR_REPO_NAME`
   - **Branch**: `main`
   - **Main file path**: `web_app.py`
4. Click "Deploy!"

### 4. Access Your App

Once deployed, you'll get a URL like:
```
https://YOUR_APP_NAME-YOUR_USERNAME.streamlit.app
```

This URL works on any device - desktop, tablet, or mobile! 📱

## 🔧 Configuration Options

### Environment Variables (Optional)

You can set environment variables in Streamlit Cloud for:
- Custom problem bank files
- API keys (if you add external features)
- Debug modes

### Custom Domain (Optional)

Streamlit Cloud supports custom domains for professional deployments.

## 📱 Mobile Optimization

The app is already optimized for mobile with:
- Touch-friendly buttons
- Responsive layout
- Mobile-optimized text sizes
- Full-width buttons
- Simplified navigation

## 🔄 Updating Your App

To update your deployed app:
1. Make changes to your code
2. Commit and push to GitHub
3. Streamlit Cloud automatically redeploys!

## 🐛 Troubleshooting

### Common Issues:

1. **Import Errors**: Check that all dependencies are in `requirements.txt`
2. **File Not Found**: Ensure `problem_bank.yaml` is in the root directory
3. **App Won't Start**: Check the logs in Streamlit Cloud dashboard

### Getting Help:

- Check Streamlit Cloud logs for error messages
- Verify your `requirements.txt` has correct versions
- Ensure all Python files are properly formatted

## 🎯 Quick Deploy Checklist

- [ ] Code pushed to GitHub
- [ ] `requirements.txt` includes all dependencies
- [ ] `web_app.py` is the main file
- [ ] `.streamlit/config.toml` exists
- [ ] Repository is public (or you have Streamlit Cloud Pro)
- [ ] All files are in the root directory

## 🚀 Alternative Deployment Options

### Railway
```bash
# Create railway.json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "streamlit run web_app.py --server.port $PORT"
  }
}
```

### Heroku
```bash
# Create Procfile
web: streamlit run web_app.py --server.port $PORT --server.address 0.0.0.0
```

### Docker
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "web_app.py", "--server.address", "0.0.0.0"]
```

## 📊 Monitoring

Streamlit Cloud provides:
- Usage analytics
- Performance metrics
- Error logs
- Deployment history

## 🔒 Security

For production use:
- Set up authentication if needed
- Use environment variables for secrets
- Regular security updates
- Monitor usage patterns

---

**Ready to deploy?** Just follow steps 1-3 above and you'll have your mobile-accessible coding interview practice system live in minutes! 🎉
