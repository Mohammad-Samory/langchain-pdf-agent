# Testing the PDF Q&A Agent

## Using the API

### 1. Start the Service

```bash
docker-compose up pdf-agent
```

Wait for: `Application startup complete`

### 2. Test with a Sample PDF

You can test with any PDF document. Here are some free resources:

- **Academic Papers**: https://arxiv.org/
- **Books**: https://www.gutenberg.org/
- **Reports**: Search for "PDF annual report" for any company

### 3. Upload Example

```bash
# Upload your PDF
curl -X POST "http://localhost:8200/api/upload" \
  -F "file=@/path/to/your/document.pdf"

# Expected response:
# {
#   "status": "success",
#   "filename": "document.pdf",
#   "total_pages": 25,
#   "total_chunks": 150,
#   "message": "PDF 'document.pdf' successfully uploaded and indexed"
# }
```

### 4. Query Examples

```bash
# General summary
curl -X POST "http://localhost:8200/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'

# Specific information
curl -X POST "http://localhost:8200/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the key findings?"}'

# Follow-up question
curl -X POST "http://localhost:8200/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Can you elaborate on the methodology?"}'

# Specific page reference
curl -X POST "http://localhost:8200/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What does page 5 discuss?"}'
```

## Using the CLI

```bash
# Upload
python ask.py --upload document.pdf

# Ask questions
python ask.py -q "What is the main topic?"
python ask.py -q "Summarize the conclusions"

# View conversation
python ask.py --history

# Document info
python ask.py --info

# Clear conversation (keep document)
python ask.py --clear

# Clear everything
python ask.py --clear-all
```

## Using Swagger UI

1. Open browser: http://localhost:8200/docs
2. Try the `/api/upload` endpoint
   - Click "Try it out"
   - Choose file
   - Execute
3. Try the `/api/ask` endpoint
   - Click "Try it out"
   - Enter question
   - Execute

## Expected Behavior

### Good Questions:

- "What is the main topic of this document?"
- "Summarize the key findings"
- "What methodology was used?"
- "What are the conclusions?"
- "Can you explain section X?"

### Agent Behavior:

1. Receives question
2. Decides to search the PDF (calls vector search tool)
3. Gets relevant chunks with page numbers
4. Synthesizes answer from chunks
5. Returns answer with page citations

### Example Response:

```json
{
  "answer": "According to the document, the main topic is machine learning applications in healthcare. The study, described on Page 3, focuses on using neural networks for disease prediction. The key findings on Page 7 show an accuracy improvement of 15% over traditional methods.",
  "sources": [
    { "page": 3, "type": "reference" },
    { "page": 7, "type": "reference" }
  ]
}
```

## Troubleshooting Tests

### No results found?

- Check if PDF was uploaded successfully
- Try more specific questions
- Verify PDF has readable text (not scanned images)

### Slow responses?

- First query is slower (model initialization)
- Subsequent queries are faster
- Adjust `k` parameter for fewer chunks

### Errors?

```bash
# Check logs
docker-compose logs pdf-agent

# Check if OpenAI key is set
docker-compose exec pdf-agent env | grep OPENAI

# Restart service
docker-compose restart pdf-agent
```

## Performance Tips

1. **Chunk Size**: Larger chunks (1500) for detailed answers, smaller (500) for precise answers
2. **Overlap**: More overlap (300) for better context, less (100) for speed
3. **Model**: `gpt-4` for accuracy, `gpt-3.5-turbo` for speed
4. **Temperature**: 0.0 for factual, 0.7 for creative

Adjust in `.env`:

```env
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.0
```

## Sample Test Cases

### Test Case 1: Simple Question

```bash
Question: "What is this document about?"
Expected: General summary with page references
```

### Test Case 2: Specific Information

```bash
Question: "What are the main findings?"
Expected: Detailed findings with multiple page citations
```

### Test Case 3: Follow-up

```bash
Question 1: "What methodology was used?"
Question 2: "Why was this approach chosen?"
Expected: Agent uses conversation history for context
```

### Test Case 4: Page-Specific

```bash
Question: "What does page 5 discuss?"
Expected: Focused answer about page 5 content
```

### Test Case 5: Not in Document

```bash
Question: "What is the price of Bitcoin?"
Expected: "This information is not in the document"
```

## Verification Checklist

- [ ] Service starts without errors
- [ ] PDF uploads successfully
- [ ] First question gets answered
- [ ] Follow-up questions work
- [ ] Page numbers are cited
- [ ] Conversation history maintained
- [ ] Swagger UI accessible
- [ ] CLI script works
- [ ] Can clear conversation
- [ ] Can upload new PDF

---

**Happy Testing! 🧪**
