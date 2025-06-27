# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AID Commander v4.1 is a knowledge graph-enhanced AI development orchestrator that provides 92%+ certainty through multi-layer validation, hallucination detection, and temporal pattern recognition. It extends the v4.0 system with comprehensive knowledge graphs, hybrid RAG systems, and bulletproof validation.

## Build and Development Commands

### Installation
```bash
# Install with all dependencies
pip install -e ".[all]"

# Install specific feature sets
pip install -e ".[dev]"        # Development tools
pip install -e ".[enterprise]" # Enterprise features
pip install -e ".[ml]"         # ML dependencies
```

### Infrastructure Management
```bash
# Start all services (Neo4j, Redis, ChromaDB, Elasticsearch, etc.)
cd infrastructure/docker && docker-compose up -d

# Check service health
docker-compose ps
aid-kg health-check

# Stop all services
docker-compose down
```

### Testing Commands
```bash
# Run comprehensive test suite
python test_comprehensive.py

# Run specific test categories
pytest tests/test_hallucination_detection.py -v
pytest tests/test_knowledge_graph.py -v
pytest tests/test_multi_layer_validation.py -v
pytest tests/test_integration.py -v --integration

# Code formatting and linting
black aid_commander_v41/
ruff check aid_commander_v41/
mypy aid_commander_v41/
```

### Knowledge Graph Management
```bash
# Initialize knowledge graphs
aid-kg init-neo4j
aid-kg init-graphiti
aid-kg init-chromadb

# Add framework knowledge
aid-kg add-framework pydantic-ai --auto-discover
aid-kg add-framework fastapi --auto-discover

# Validate knowledge graph integrity
aid-kg validate-knowledge-graph
```

### CLI Commands
```bash
# Initialize project with knowledge graphs
aid-commander-v41 init --with-knowledge-graphs

# Generate validated code
aid-commander-v41 start --project-name <name> --framework pydantic-ai --with-validation

# Run hallucination detection
aid-kg detect-hallucinations path/to/code.py --auto-correct

# Multi-layer validation
aid-validate generate-code --intent "Create AI agent" --framework pydantic-ai --confidence-threshold 0.92
```

## Architecture Overview

### Core Components
- **Knowledge Graph System**: Neo4j (structural), Graphiti (temporal), ChromaDB (vector embeddings)
- **6-Layer Validation Engine**: Structural, temporal, documentation, memory, type safety, and consensus validation
- **Hallucination Detection**: 95%+ accuracy detection of non-existent APIs and methods
- **Enhanced Memory Bank**: Graph-augmented context with cross-project learning
- **Hybrid RAG System**: Vector + graph search for documentation validation

### Key Modules
- `aid_commander_v41/cli/main.py`: Enhanced CLI with knowledge graph validation (AIDCommanderV41 class)
- `knowledge_graph/graphiti/temporal_engine.py`: Temporal pattern recognition and decision tracking
- `knowledge_graph/neo4j/graph_client.py`: Structural API validation and relationship mapping
- `knowledge_graph/rag/hybrid_search.py`: Hybrid vector and graph search system
- `validation/multi_layer/validation_engine.py`: 6-layer consensus validation system
- `validation/hallucination/detection_engine.py`: AI hallucination detection and correction
- `memory_enhanced/graph_memory_bank.py`: Graph-enhanced memory with cross-project learning

### Infrastructure Services
- **Neo4j**: Graph database for API relationships and structural validation
- **Redis**: Caching and session management for Graphiti temporal engine
- **ChromaDB**: Vector embeddings for RAG system
- **Elasticsearch**: Advanced search capabilities
- **PostgreSQL**: Enhanced memory bank storage
- **Prometheus/Grafana**: Monitoring and metrics

## Development Patterns

### 92%+ Confidence Protocol
All code generation follows a 6-layer validation system:
1. **Structural Validation**: Verify APIs exist in Neo4j knowledge graph
2. **Temporal Validation**: Check historical success patterns via Graphiti
3. **Documentation Validation**: Match against official documentation via RAG
4. **Memory Validation**: Align with past successful decisions
5. **Type Safety Validation**: Ensure proper type annotations via Pydantic AI
6. **Consensus Validation**: Calculate weighted agreement across all layers

### Knowledge Graph Intelligence
- APIs must exist in Neo4j graph before code generation
- Temporal patterns from Graphiti inform success probability
- Cross-framework learning prevents API confusion
- Real-time knowledge graph updates from usage patterns

### Hallucination Prevention
- Multi-source validation catches 95%+ of hallucinated APIs
- Framework-specific knowledge graphs prevent mixing incompatible APIs
- Automatic correction suggests validated alternatives
- Pattern recognition identifies common hallucination types

## Configuration

### Environment Variables
```bash
# Knowledge Graph Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=aid-commander-v41-secure
REDIS_URL=redis://localhost:6379
CHROMA_PERSIST_DIR=./chroma_db

# Validation Thresholds
QUALITY_SUCCESS_THRESHOLD=92
HALLUCINATION_THRESHOLD=0.3
CONFIDENCE_THRESHOLD=0.92

# Performance Settings
KNOWLEDGE_GRAPH_ENABLED=true
MEMORY_BANK_ENABLED=true
KNOWLEDGE_GRAPH_CACHE_TTL=3600
```

### Docker Services
The system requires multiple services running via docker-compose:
- Neo4j (ports 7474, 7687) for structural knowledge graphs
- Redis (port 6379) for temporal engine caching
- ChromaDB (port 8000) for vector embeddings
- Elasticsearch (port 9200) for advanced search
- PostgreSQL (port 5432) for memory bank storage

## Testing Strategy

### Test Categories
- **Comprehensive Testing**: `test_comprehensive.py` validates entire system
- **Knowledge Graph Tests**: Verify Neo4j, Graphiti, and RAG system integration
- **Validation Engine Tests**: Test 6-layer validation and consensus scoring
- **Hallucination Detection**: Validate 95%+ detection accuracy
- **Integration Tests**: End-to-end testing with real infrastructure

### Current Test Status
The system maintains 97.1% test success rate (34/35 tests passing) with comprehensive validation across all components.

## Troubleshooting

### Common Issues
```bash
# Import hanging issues (resolved with lazy loading)
# Check aid_commander_v41/__init__.py for lazy import patterns

# Missing dependencies
pip install structlog neo4j chromadb sentence-transformers pytest-asyncio

# Docker services not running
cd infrastructure/docker && docker-compose up -d

# Knowledge graph not initialized
aid-kg init-neo4j && aid-kg init-graphiti && aid-kg init-chromadb
```

### Performance Optimization
```bash
# Enable caching
export KNOWLEDGE_GRAPH_CACHE_TTL=3600
export NEO4J_MAX_CONNECTION_POOL_SIZE=50

# Parallel processing
aid-kg detect-hallucinations src/ --parallel-workers 8
```