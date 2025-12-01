# Architecture Diagrams

This directory contains PlantUML and Mermaid diagram source files.

## Viewing the Diagrams

### Option 1: Online Viewers
- **PlantUML (.puml files):** https://www.plantuml.com/plantuml/uml/
- **Mermaid (.mmd files):** https://mermaid.live/

### Option 2: VS Code Extensions
- Install "PlantUML" extension by jebbs
- Install "Markdown Preview Mermaid Support" extension

### Option 3: Generate PNG Files
```bash
# Install PlantUML (requires Java)
brew install plantuml  # macOS
apt-get install plantuml  # Ubuntu

# Generate images
plantuml *.puml
```

## Diagram Descriptions

### system_architecture.puml
High-level system architecture showing all components and their interactions.

### localstack_deployment.puml
Docker Compose deployment architecture for LocalStack environment.

### aws_deployment.puml
AWS production deployment with VPC, subnets, and managed services.

### async_order_flow.puml
Sequence diagram showing the asynchronous order processing flow.

### cost_comparison.mmd
Mermaid chart comparing costs between LocalStack and AWS.

## Embedding in Markdown

For GitHub README:
```markdown
![Architecture](./diagrams/system_architecture.png)
```

For documentation:
- Export as PNG/SVG from online viewers
- Commit generated images to repository