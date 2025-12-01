#!/usr/bin/env python3
"""
Architecture Diagram Generator
Creates visual diagrams for documentation
"""

import os

def generate_diagrams():
    """Generate architecture diagrams using PlantUML-style text"""
    
    diagrams_dir = "./diagrams"
    os.makedirs(diagrams_dir, exist_ok=True)
    
    # System Architecture Diagram
    system_architecture = """
@startuml system_architecture
!define RECTANGLE class

title Asynchronous Order Processing System Architecture

actor Client as client
rectangle "Order API\\n(Go/Gin)" as api
rectangle "SNS Topic\\n(order-events)" as sns
rectangle "SQS Queue\\n(order-queue)" as sqs
rectangle "Order Worker\\n(Go)" as worker
database "CloudWatch\\nLogs" as logs

client -down-> api : POST /orders/async
api -down-> sns : Publish order event
sns -down-> sqs : Fan-out subscription
worker -up-> sqs : Long-poll messages
api -right-> logs : Application logs
worker -right-> logs : Processing logs

note right of api
  • REST API
  • Gin framework
  • SNS publisher
  • 3s payment bottleneck
end note

note right of worker
  • SQS consumer
  • Configurable workers
  • Message processing
  • Auto-deletion
end note

@enduml
"""
    
    # LocalStack Deployment Diagram
    localstack_deployment = """
@startuml localstack_deployment
!define RECTANGLE class

title LocalStack Deployment Architecture

package "Docker Compose Network" {
    rectangle "LocalStack\\nContainer" as ls {
        component "SNS" as sns
        component "SQS" as sqs
        component "CloudWatch" as cw
    }
    
    rectangle "Order API\\nContainer" as api {
        component "Gin Server\\n:8081" as gin
    }
    
    rectangle "Order Worker\\nContainer" as worker {
        component "SQS Consumer\\n(1 instance)" as consumer
    }
    
    gin -down-> sns : Publish
    sns -down-> sqs : Subscribe
    consumer -up-> sqs : Poll
    gin -right-> cw : Metrics
    consumer -right-> cw : Logs
}

actor "External\\nClient" as client
client -down-> gin : :8080 (mapped)

note bottom of ls
  • Port 4566 (LocalStack gateway)
  • Zero cloud costs
  • Offline capable
  • Fast iteration
end note

@enduml
"""
    
    # AWS Deployment Diagram
    aws_deployment = """
@startuml aws_deployment
!define RECTANGLE class

title AWS Production Deployment Architecture

package "VPC (10.0.0.0/16)" {
    
    package "Public Subnets" {
        rectangle "Application\\nLoad Balancer" as alb
        rectangle "NAT Gateway" as nat
        rectangle "Internet\\nGateway" as igw
    }
    
    package "Private Subnets" {
        rectangle "ECS Fargate" as ecs {
            component "Order API\\nTask" as api_task
            component "Order Worker\\nTask" as worker_task
        }
    }
    
    alb -down-> api_task : Forward :8081
    api_task -up-> nat : Egress
    worker_task -up-> nat : Egress
    nat -up-> igw : Internet
}

cloud "AWS Managed Services" {
    component "SNS Topic" as sns
    component "SQS Queue" as sqs
    component "CloudWatch" as cw
    component "ECR" as ecr
}

actor "Internet\\nClients" as clients
clients -down-> igw : HTTP :80
igw -down-> alb

api_task -right-> sns : Publish
sns -down-> sqs : Subscribe
worker_task -left-> sqs : Poll
api_task -down-> cw : Logs
worker_task -down-> cw : Logs
ecs -up-> ecr : Pull images

note right of ecs
  • Auto-scaling enabled
  • Multi-AZ deployment
  • 0.25 vCPU / 512 MB
  • Fargate serverless
end note

@enduml
"""
    
    # Sequence Diagram - Async Order Flow
    async_flow = """
@startuml async_order_flow
!define RECTANGLE class

title Asynchronous Order Processing Flow

actor Client
participant "Order API" as API
participant "SNS Topic" as SNS
participant "SQS Queue" as SQS
participant "Order Worker" as Worker
database "CloudWatch" as CW

Client -> API : POST /orders/async\\n{order_data}
activate API

API -> API : Generate order_id
API -> API : Set status = "pending"

API -> SNS : Publish order event
activate SNS
SNS --> API : Message ID
deactivate SNS

API --> Client : 202 Accepted\\n{order_id, status}
deactivate API

SNS -> SQS : Fan-out message
activate SQS

Worker -> SQS : Long-poll (20s)
SQS --> Worker : Order message
activate Worker

Worker -> Worker : Process payment\\n(3 seconds)
Worker -> Worker : Update status = "completed"

Worker -> SQS : Delete message
deactivate SQS

Worker -> CW : Log completion
deactivate Worker

note over API
  Fast response to client
  (~50ms average)
end note

note over Worker
  Async processing
  (~3 seconds)
end note

@enduml
"""
    
    # Cost Comparison Chart (Mermaid)
    cost_comparison = """
graph LR
    A[Cost Analysis] --> B[LocalStack: $0/month]
    A --> C[AWS: $41/month]
    
    B --> B1[Zero infrastructure]
    B --> B2[Local compute only]
    B --> B3[No data transfer]
    
    C --> C1[ECS: $15]
    C --> C2[ALB + NAT: $25]
    C --> C3[Logs: $1]
    
    style B fill:#2ecc71
    style C fill:#e74c3c
"""
    
    # Write all diagrams
    diagrams = {
        'system_architecture.puml': system_architecture,
        'localstack_deployment.puml': localstack_deployment,
        'aws_deployment.puml': aws_deployment,
        'async_order_flow.puml': async_flow,
        'cost_comparison.mmd': cost_comparison
    }
    
    for filename, content in diagrams.items():
        filepath = os.path.join(diagrams_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content.strip())
        print(f"✓ Generated: {filepath}")
    
    # Create README for diagrams
    diagram_readme = """# Architecture Diagrams

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
"""
    
    readme_path = os.path.join(diagrams_dir, 'README.md')
    with open(readme_path, 'w') as f:
        f.write(diagram_readme.strip())
    print(f"✓ Generated: {readme_path}")
    
    print(f"\n{'='*60}")
    print("✓ All diagrams generated successfully!")
    print(f"{'='*60}\n")
    print(f"Output directory: {diagrams_dir}/")
    print("\nTo view diagrams:")
    print("  1. Visit https://www.plantuml.com/plantuml/uml/")
    print("  2. Copy and paste the .puml file contents")
    print("  3. Export as PNG for documentation")
    print("")

if __name__ == '__main__':
    generate_diagrams()
