# Streamlit Cloud Deployment Guide

This guide will help you deploy your GitLab AI Chatbot on Streamlit Cloud.

## Prerequisites

1. **GitHub Repository**: Your code should be in a GitHub repository
2. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **Google API Key**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Step 1: Prepare Your Repository

### 1.1 Ensure Required Files Exist
Make sure these files are in your repository root:
- `app.py` (main Streamlit app)
- `requirements.txt` (Python dependencies)
- `.streamlit/config.toml` (Streamlit configuration)
- All your source code in `src/` and `components/` directories

### 1.2 Data Files
Ensure your data files are included:
- `data/chroma_db/` (vector database)
- `data/documents.json`
- `data/chunks.json`

## Step 2: Deploy on Streamlit Cloud

### 2.1 Connect Your Repository
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub account
4. Select your repository: `gitlab-chatbot`
5. Set the main file path: `app.py`

### 2.2 Configure Secrets
In the Streamlit Cloud interface, go to "Settings" → "Secrets" and add:

```toml
GOOGLE_API_KEY = "your_actual_google_api_key_here"
```

**Important**: Replace `your_actual_google_api_key_here` with your real Google API key.

### 2.3 Advanced Settings (Optional)
- **Python version**: 3.9 or higher
- **Memory**: Default should work, but you can increase if needed
- **Timeout**: 300 seconds (default)

## Step 3: Deploy

1. Click "Deploy!"
2. Wait for the deployment to complete (usually 2-5 minutes)
3. Your app will be available at: `https://your-app-name.streamlit.app`

## Step 4: Verify Deployment

1. Open your deployed app
2. Check that the chatbot initializes properly
3. Test with a sample question like "What are GitLab's core values?"
4. Verify that the analytics dashboard works

## Troubleshooting

### Common Issues

1. **SQLite Version Error**
   - **Fixed**: The app now includes `pysqlite3-binary` and SQLite version fixes
   - If you still see SQLite errors, ensure `pysqlite3-binary` is in requirements.txt

2. **API Key Error**
   - The API key is hardcoded in the app, so this should not occur
   - If you need to change the API key, edit `app.py` line 51

3. **Import Errors**
   - Verify all dependencies are in `requirements.txt`
   - Check that all Python files are properly structured

4. **Data Loading Issues**
   - Ensure all data files are committed to your repository
   - Check file paths in your code

5. **Memory Issues**
   - Increase memory allocation in Streamlit Cloud settings
   - Consider optimizing your vector database size

### Debugging

1. Check the Streamlit Cloud logs in the "Logs" tab
2. Use `st.write()` statements to debug locally
3. Test your app locally first: `streamlit run app.py`

## Local Development

To run the app locally:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your API key in `.streamlit/secrets.toml`:
   ```toml
   GOOGLE_API_KEY = "your_api_key_here"
   ```

3. Run the app:
   ```bash
   streamlit run app.py
   ```

## Security Notes

- Never commit API keys to your repository
- Use Streamlit secrets for sensitive information
- Regularly rotate your API keys
- Monitor your API usage

## Performance Optimization

1. **Vector Database**: Consider using a cloud vector database for better performance
2. **Caching**: The app includes response caching for better performance
3. **Memory**: Monitor memory usage and adjust Streamlit Cloud settings if needed

## Support

If you encounter issues:
1. Check the Streamlit Cloud documentation
2. Review the app logs
3. Test locally first
4. Check the GitHub repository for any issues

## Next Steps

After successful deployment:
1. Share your app URL with users
2. Monitor usage and performance
3. Consider adding authentication if needed
4. Set up monitoring and alerts
