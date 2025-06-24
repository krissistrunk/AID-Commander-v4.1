# 🧠 AID Commander v4.1 - Knowledge Graph Setup Guide

**Complete setup and configuration of Neo4j, Graphiti, and RAG systems**

## 🎯 Overview

AID Commander v4.1 uses a three-layer knowledge graph system:
- **Neo4j**: Structural relationships (APIs, classes, methods)
- **Graphiti**: Temporal patterns (what worked when)
- **RAG System**: Documentation and usage validation

## 🏗️ Infrastructure Setup

### Docker Infrastructure (Recommended)
```bash
# Navigate to infrastructure directory
cd infrastructure/docker

# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps

# Expected output:
# NAME                    STATUS              PORTS
# aid-neo4j              Up                  7474/tcp, 7687/tcp
# aid-redis              Up                  6379/tcp
# aid-chromadb           Up                  8000/tcp
# aid-elasticsearch      Up                  9200/tcp, 9300/tcp
# aid-grafana            Up                  3000/tcp
# aid-prometheus         Up                  9090/tcp
```

### Manual Installation (Advanced)

#### Neo4j Setup
```bash
# Install Neo4j Desktop or Server
# Download from: https://neo4j.com/download/

# Or use Docker directly
docker run \
  --name aid-neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/aid-commander-v41-secure \
  -e NEO4J_PLUGINS='["apoc"]' \
  -v neo4j_data:/data \
  neo4j:5.13
```

#### Redis Setup
```bash
# Install Redis
# Ubuntu/Debian: apt install redis-server
# macOS: brew install redis
# Windows: Download from redis.io

# Or use Docker
docker run \
  --name aid-redis \
  -p 6379:6379 \
  -v redis_data:/data \
  redis:7-alpine
```

#### ChromaDB Setup
```bash
# Install ChromaDB
pip install chromadb

# Or use Docker
docker run \
  --name aid-chromadb \
  -p 8000:8000 \
  -v chromadb_data:/chroma/chroma \
  chromadb/chroma:0.4.15
```

## ⚙️ Configuration

### Environment Variables
```bash
# Copy and edit configuration
cp .env.template .env
nano .env

# Required configuration:
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=aid-commander-v41-secure
NEO4J_DATABASE=neo4j

# Redis Configuration  
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=  # Optional
REDIS_DB=0

# ChromaDB Configuration
CHROMA_URL=http://localhost:8000
CHROMA_PERSIST_DIR=./chroma_db

# Elasticsearch Configuration (Optional)
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_USERNAME=  # Optional
ELASTICSEARCH_PASSWORD=  # Optional

# Performance Configuration
KNOWLEDGE_GRAPH_CACHE_TTL=3600
KNOWLEDGE_GRAPH_MAX_CONNECTIONS=10
KNOWLEDGE_GRAPH_TIMEOUT=30
```

### Advanced Configuration
```python
# config/knowledge_graph.yaml
knowledge_graph:
  neo4j:
    uri: ${NEO4J_URI}
    username: ${NEO4J_USERNAME}
    password: ${NEO4J_PASSWORD}
    database: ${NEO4J_DATABASE}
    max_connection_lifetime: 3600
    max_connection_pool_size: 50
    connection_acquisition_timeout: 60
    
  graphiti:
    redis_url: ${REDIS_URL}
    embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
    temporal_resolution: "day"
    max_temporal_edges: 1000
    
  rag:
    chroma:
      url: ${CHROMA_URL}
      collection_name: "aid_commander_docs"
      embedding_function: "all-MiniLM-L6-v2"
      distance_metric: "cosine"
    
    elasticsearch:
      url: ${ELASTICSEARCH_URL}
      index_name: "aid_commander_knowledge"
      
  performance:
    cache_enabled: true
    cache_ttl: 3600
    parallel_workers: 4
    batch_size: 100
```

## 🗃️ Neo4j Knowledge Graph Setup

### Initialize Schema
```bash
# Initialize Neo4j knowledge graph schema
aid-kg init-neo4j

# This creates the following node types:
# - Framework, Class, Method, Function, Parameter
# - Pattern, UseCase, Documentation, Example
# - Project, Decision, Outcome
```

### Schema Overview
```cypher
// Framework structure
CREATE (f:Framework {name: "pydantic-ai", version: "0.0.8"})
CREATE (c:Class {name: "Agent", framework: "pydantic-ai"})
CREATE (m:Method {name: "run_sync", class: "Agent", returns: "RunResult"})
CREATE (p:Parameter {name: "user_prompt", type: "str", required: true})

// Relationships
CREATE (f)-[:HAS_CLASS]->(c)
CREATE (c)-[:HAS_METHOD]->(m)
CREATE (m)-[:HAS_PARAMETER]->(p)

// Pattern structure
CREATE (pattern:Pattern {
  name: "basic_agent_setup",
  framework: "pydantic-ai",
  success_rate: 0.94,
  usage_count: 156
})

CREATE (example:Example {
  code: "agent = Agent('openai:gpt-4', result_type=Response)",
  pattern: "basic_agent_setup"
})

CREATE (pattern)-[:HAS_EXAMPLE]->(example)
```

### Load Framework Data
```bash
# Load Pydantic AI framework knowledge
aid-kg load-framework pydantic-ai \
  --source official-docs \
  --github-repo pydantic/pydantic-ai

# Load FastAPI framework knowledge  
aid-kg load-framework fastapi \
  --source official-docs \
  --github-repo tiangolo/fastapi

# Load custom framework
aid-kg load-framework my-framework \
  --source docs-url \
  --url https://my-framework.dev/docs
```

### Verify Neo4j Setup
```bash
# Check Neo4j connection
aid-kg test-neo4j

# View loaded frameworks
aid-kg list-frameworks

# Get framework statistics
aid-kg neo4j-stats

# Example output:
# 📊 Neo4j Knowledge Graph Statistics:
# 🏗️  Frameworks: 3 (pydantic-ai, fastapi, django)
# 📦 Classes: 127
# 🔧 Methods: 1,234  
# 📄 Documentation Nodes: 2,456
# 🎯 Patterns: 89
# 💡 Examples: 456
```

## ⏰ Graphiti Temporal Knowledge Graph

### Initialize Graphiti
```bash
# Initialize Graphiti temporal knowledge graph
aid-kg init-graphiti

# Configure temporal resolution
aid-kg configure-graphiti \
  --temporal-resolution day \
  --max-temporal-edges 1000 \
  --embedding-model sentence-transformers/all-MiniLM-L6-v2
```

### Understanding Temporal Patterns
```python
# Example temporal pattern storage
await graphiti_engine.store_pattern(
    pattern_name="pydantic_ai_agent_creation",
    framework="pydantic-ai", 
    pattern_type="initialization",
    code_template="Agent('{model}', result_type={result_type})",
    success_rate=0.94,
    use_cases=["chatbot", "data_processing", "code_analysis"],
    temporal_context={
        "created_at": "2024-01-15",
        "project_phase": "initial_setup", 
        "team_size": 3,
        "complexity": "medium"
    }
)
```

### Query Temporal Patterns
```bash
# Get pattern evolution over time
aid-kg query-temporal \
  --pattern "agent_creation" \
  --framework pydantic-ai \
  --time-range "last_6_months"

# Find patterns that improved over time
aid-kg temporal-trends \
  --min-improvement 0.1 \
  --frameworks pydantic-ai,fastapi

# Example output:
# 📈 Temporal Pattern Analysis:
# 🎯 Pattern: "async_agent_usage"
#    Jan 2024: 67% success rate
#    Jun 2024: 89% success rate  
#    Improvement: +22% (likely due to better error handling)
```

### Temporal Decision Tracking
```bash
# Store development decisions with temporal context
aid-kg store-decision \
  --decision "Use sync Agent.run_sync for simple cases" \
  --framework pydantic-ai \
  --context "Customer support chatbot" \
  --outcome "95% success rate" \
  --temporal-tags "project_start,simple_use_case"
```

## 🔍 RAG System Setup

### ChromaDB Collection Setup
```bash
# Initialize ChromaDB collections
aid-kg init-chromadb

# Load documentation into ChromaDB
aid-kg load-docs-to-chroma \
  --framework pydantic-ai \
  --source https://ai.pydantic.dev \
  --collection aid_commander_docs

# Verify collection
aid-kg chroma-stats

# Example output:
# 📚 ChromaDB Collections:
# 📖 aid_commander_docs: 1,234 documents
# 🎯 pydantic_ai_patterns: 89 patterns
# 💡 code_examples: 456 examples
```

### Elasticsearch Setup (Optional)
```bash
# Initialize Elasticsearch index
aid-kg init-elasticsearch

# Load documentation to Elasticsearch  
aid-kg load-docs-to-elasticsearch \
  --framework pydantic-ai \
  --index aid_commander_knowledge

# Create optimized mappings
aid-kg create-elasticsearch-mappings
```

### Hybrid Search Configuration
```python
# config/rag_system.yaml
rag_system:
  vector_search:
    provider: "chromadb"
    embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
    top_k: 10
    score_threshold: 0.7
    
  keyword_search:
    provider: "elasticsearch"  # or "simple"
    top_k: 5
    boost_exact_matches: true
    
  hybrid_fusion:
    method: "rrf"  # Reciprocal Rank Fusion
    vector_weight: 0.7
    keyword_weight: 0.3
    
  caching:
    enabled: true
    ttl: 1800  # 30 minutes
    max_entries: 10000
```

### Test RAG System
```bash
# Test hybrid search
aid-kg test-rag \
  --query "how to create pydantic ai agent" \
  --framework pydantic-ai

# Example output:
# 🔍 Hybrid Search Results:
# 
# 📄 Vector Search (ChromaDB):
# 1. "Creating Your First Agent" (score: 0.89)
# 2. "Agent Configuration Options" (score: 0.84) 
# 3. "Result Types and Validation" (score: 0.81)
# 
# 🔎 Keyword Search (Elasticsearch):
# 1. "Agent class documentation" (score: 0.92)
# 2. "pydantic-ai quickstart" (score: 0.87)
# 
# 🎯 Hybrid Result:
# "Creating Your First Agent" (combined score: 0.91)
```

## 🔧 Framework Integration

### Loading Framework Knowledge

#### Automatic Loading (Recommended)
```bash
# Load from official documentation
aid-kg add-framework pydantic-ai --auto-discover

# This will:
# 1. Fetch documentation from official sources
# 2. Parse API structure with AST analysis
# 3. Create Neo4j nodes and relationships
# 4. Generate examples and patterns
# 5. Load documentation into RAG system
```

#### Manual Loading
```bash
# Load from specific sources
aid-kg add-framework my-framework \
  --docs-url https://my-framework.dev/docs \
  --github-repo my-org/my-framework \
  --pypi-package my-framework \
  --examples-dir ./examples/

# Load from local documentation
aid-kg add-framework local-framework \
  --local-docs ./docs/ \
  --source-code ./src/ \
  --examples ./examples/
```

### Custom Framework Definition
```yaml
# frameworks/my_framework.yaml
name: "my-framework"
version: "1.0.0"
description: "Custom AI framework"

classes:
  - name: "MyAgent"
    methods:
      - name: "process"
        parameters:
          - name: "input"
            type: "str"
            required: true
        returns: "ProcessResult"
        
patterns:
  - name: "basic_usage"
    template: |
      agent = MyAgent(config={config})
      result = agent.process({input})
    success_rate: 0.85
    use_cases: ["data_processing", "text_analysis"]

documentation:
  base_url: "https://my-framework.dev"
  api_reference: "/api"
  examples: "/examples"
```

## 📊 Monitoring and Maintenance

### Health Checks
```bash
# Check all knowledge graph services
aid-kg health-check

# Individual service checks
aid-kg health-check --service neo4j
aid-kg health-check --service redis  
aid-kg health-check --service chromadb

# Automated health monitoring
aid-kg start-health-monitor \
  --interval 60 \
  --alert-webhook https://hooks.slack.com/...
```

### Performance Monitoring
```bash
# View performance metrics
aid-kg metrics

# Example output:
# 📊 Knowledge Graph Performance:
# 🗃️  Neo4j Query Time: avg 45ms, p95 120ms
# ⚡ Redis Cache Hit Rate: 94%
# 🔍 ChromaDB Search Time: avg 89ms, p95 200ms
# 🧠 Hybrid RAG Response Time: avg 150ms, p95 350ms
```

### Data Backup and Restore
```bash
# Backup knowledge graphs
aid-kg backup \
  --output /backups/aid-kg-$(date +%Y%m%d).tar.gz \
  --include neo4j,redis,chromadb

# Restore from backup
aid-kg restore \
  --backup /backups/aid-kg-20240615.tar.gz \
  --confirm

# Automated backup schedule
aid-kg schedule-backup \
  --frequency daily \
  --retention 30 \
  --storage s3://my-bucket/aid-backups/
```

### Knowledge Graph Updates
```bash
# Update framework knowledge
aid-kg update-framework pydantic-ai

# Update all frameworks
aid-kg update-all-frameworks

# Schedule automatic updates
aid-kg schedule-updates \
  --frequency weekly \
  --frameworks pydantic-ai,fastapi \
  --notify-webhook https://hooks.slack.com/...
```

## 🚀 Performance Optimization

### Connection Pooling
```python
# Neo4j connection optimization
NEO4J_MAX_CONNECTION_POOL_SIZE=50
NEO4J_CONNECTION_ACQUISITION_TIMEOUT=60
NEO4J_MAX_CONNECTION_LIFETIME=3600

# Redis connection optimization  
REDIS_CONNECTION_POOL_MAX_CONNECTIONS=20
REDIS_SOCKET_KEEPALIVE=true
REDIS_SOCKET_KEEPALIVE_OPTIONS=1,3,5
```

### Caching Strategy
```bash
# Configure multi-level caching
aid-kg configure-cache \
  --l1-cache memory \
  --l1-size 100MB \
  --l2-cache redis \
  --l2-ttl 3600 \
  --l3-cache disk \
  --l3-size 1GB
```

### Query Optimization
```cypher
-- Create indexes for better performance
CREATE INDEX framework_name FOR (f:Framework) ON (f.name);
CREATE INDEX class_name FOR (c:Class) ON (c.name);
CREATE INDEX method_name FOR (m:Method) ON (m.name);
CREATE INDEX pattern_framework FOR (p:Pattern) ON (p.framework);

-- Composite indexes for complex queries
CREATE INDEX framework_class FOR (c:Class) ON (c.framework, c.name);
```

## 🛠️ Troubleshooting

### Common Issues

#### Neo4j Connection Issues
```bash
# Check Neo4j status
docker logs aid-neo4j

# Test connection
aid-kg test-neo4j --verbose

# Reset Neo4j data (if needed)
aid-kg reset-neo4j --confirm
```

#### ChromaDB Issues  
```bash
# Check ChromaDB logs
docker logs aid-chromadb

# Rebuild collections
aid-kg rebuild-chromadb --collection aid_commander_docs

# Verify embeddings
aid-kg test-embeddings --model sentence-transformers/all-MiniLM-L6-v2
```

#### Performance Issues
```bash
# Analyze slow queries
aid-kg analyze-performance --slow-threshold 1000ms

# Check resource usage
aid-kg resource-monitor

# Optimize knowledge graph
aid-kg optimize \
  --rebuild-indexes \
  --vacuum-chromadb \
  --compact-redis
```

---

**🎯 With properly configured knowledge graphs, you're ready to achieve 92%+ certainty in your AI development!**

**Next: Explore [Multi-Layer Validation](MULTI_LAYER_VALIDATION.md) to leverage your knowledge graphs for bulletproof code generation.**