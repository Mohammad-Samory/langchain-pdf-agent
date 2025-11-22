# 🚀 Quick Start Guide - PDF Q&A Agent

Get up and running in 5 minutes!

## Step 1: Prerequisites

✅ **Docker Desktop** - Must be running  
✅ **OpenAI API Key** - Get one at https://platform.openai.com/api-keys

## Step 2: Setup Environment

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-actual-key-here
```

## Step 3: Build and Run

### Windows (PowerShell):

```powershell
# Build
docker-compose build pdf-agent

# Run
docker-compose up pdf-agent
```

### Linux/Mac:

```bash
# Build
docker-compose build pdf-agent

# Run
docker-compose up pdf-agent
```

**Wait for**: `Application startup complete` message

## Step 4: Upload a PDF

### Option A: Using curl

```bash
curl -X POST "http://localhost:8200/api/upload" \
  -F "file=@/path/to/your/document.pdf"
```

### Option B: Using PowerShell

```powershell
$file = Get-Item "C:\path\to\document.pdf"
Invoke-RestMethod -Uri "http://localhost:8200/api/upload" `
  -Method Post -Form @{file=$file}
```

### Option C: Using the CLI script

```bash
python ask.py --upload document.pdf
```

### Option D: Using Swagger UI

1. Open http://localhost:8200/docs
2. Click on `/api/upload`
3. Click "Try it out"
4. Choose file and click "Execute"

## Step 5: Ask Questions!

### Using curl:

```bash
curl -X POST "http://localhost:8200/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'
```

### Using PowerShell:

```powershell
$body = @{ question = "What is this document about?" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8200/api/ask" `
  -Method Post -Body $body -ContentType "application/json"
```

### Using the CLI script:

```bash
python ask.py -q "What is this document about?"
```

### Using Swagger UI:

1. Open http://localhost:8200/docs
2. Click on `/api/ask`
3. Click "Try it out"
4. Enter your question and click "Execute"

## 🎉 That's It!

You now have a working PDF Q&A agent!

## Example Session

```bash
# 1. Upload
python ask.py --upload research_paper.pdf
# ✅ PDF 'research_paper.pdf' successfully uploaded and indexed
#    📊 Pages: 25
#    🔢 Chunks: 150

# 2. Ask questions
python ask.py -q "What are the main findings?"
# 💬 Answer: According to the document (Page 3), the main findings are...
# 📚 Sources:
#    - Page 3
#    - Page 7

# 3. Follow-up questions
python ask.py -q "Can you explain the methodology?"
# 💬 Answer: The methodology, described on Page 5, involves...

# 4. Check conversation history
python ask.py --history
# 📜 Conversation History (4 messages):
# 🧑 User: What are the main findings?
# 🤖 Assistant: According to the document...
```

## 🔧 Troubleshooting

### Docker not starting?

```bash
# Check if Docker is running
docker ps

# If not, start Docker Desktop from Start Menu
```

### "OpenAI API key not found"?

```bash
# Make sure .env file exists and has your key
cat .env  # Linux/Mac
Get-Content .env  # Windows

# Should show:
# OPENAI_API_KEY=sk-...
```

### Port 8200 already in use?

Edit `compose.yml` and change:

```yaml
ports:
  - 8201:80 # Changed from 8200
```

## 📚 Next Steps

- Read the full [README.md](README.md) for architecture details
- Explore the API at http://localhost:8200/docs
- Check out example PDFs in the `examples/` folder (if available)
- Modify agent behavior in `pdf_agent/application/agent/pdf_qa_agent.py`

## 💡 Tips

- **Chunk Size**: Adjust `CHUNK_SIZE` in `.env` for different document types
- **Model**: Change `LLM_MODEL` to `gpt-4` for better accuracy (higher cost)
- **Temperature**: Increase `LLM_TEMPERATURE` for more creative answers
- **Vector Search**: Modify `k` parameter in search to get more/fewer results

## 🆘 Need Help?

1. Check logs: `docker-compose logs pdf-agent`
2. Check the [README.md](README.md) troubleshooting section
3. Review [LangGraph docs](https://docs.langchain.com/oss/python/langgraph/overview)

---

**Happy Querying! 🎯**
