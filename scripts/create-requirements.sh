#!/bin/bash
# Quick script to create the three requirements files

echo "Creating requirements files..."

# requirements-agent.txt
cat > requirements-agent.txt << 'EOF'
fastapi==0.109.0
uvicorn[standard]==0.27.0
langchain-google-genai==1.0.10
redis==5.0.1
httpx==0.26.0
pydantic==2.5.3
duckduckgo-search==4.1.1
EOF

echo "✅ Created requirements-agent.txt"

# requirements-coordinator.txt
cat > requirements-coordinator.txt << 'EOF'
fastapi==0.109.0
uvicorn[standard]==0.27.0
redis==5.0.1
httpx==0.26.0
pydantic==2.5.3
EOF

echo "✅ Created requirements-coordinator.txt"

# requirements-streamlit.txt
cat > requirements-streamlit.txt << 'EOF'
streamlit==1.31.0
httpx==0.26.0
redis==5.0.1
pydantic==2.5.3
EOF

echo "✅ Created requirements-streamlit.txt"

echo ""
echo "✅ All requirements files created successfully!"
echo ""
echo "Files created:"
ls -lh requirements-*.txt
