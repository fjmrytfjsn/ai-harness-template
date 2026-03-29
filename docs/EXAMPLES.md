# 設定例集

テンプレートから作成したプロジェクトでよく使用される設定例です。

## 🎯 プロジェクトタイプ別設定

### Web アプリケーション開発

```yaml
# .ai-guidance/harness.yaml
project:
  name: "my-web-app"
  type: "web-application"
  
ai:
  provider: "github-copilot"
  model: "gpt-4o"

skills:
  enable:
    - code_review
    - security_check
    - performance_analysis
  
  custom:
    - name: "react_component_review"
      description: "React コンポーネントの品質チェック"
      triggers: ["React", "コンポーネント", "JSX"]
```

### API サーバー開発

```yaml
project:
  name: "my-api-server"
  type: "api-server"
  
middleware:
  stack:
    - security      # API セキュリティ特化
    - performance   # レスポンス時間最適化
    - monitoring    # API メトリクス収集

skills:
  enable:
    - code_review
    - api_documentation
    - load_testing
```

### データ分析プロジェクト

```yaml
project:
  name: "data-analysis"
  type: "data-science"
  
ai:
  provider: "openai"
  model: "gpt-4o"
  
skills:
  enable:
    - code_review
    - data_validation
    - visualization_check
    
  custom:
    - name: "notebook_review"
      description: "Jupyter Notebook の品質チェック"
      file_patterns: ["*.ipynb"]
```

## 🏢 組織・チーム別設定

### スタートアップ（高速開発重視）

```yaml
harness:
  agent_loop:
    max_iterations: 30
    timeout_seconds: 120
    enable_parallel_tools: true
    
middleware:
  stack:
    - context
    - tools
    - monitoring   # 最低限のスタック
    
ai:
  provider: "github-copilot"  # 開発効率最優先
```

### エンタープライズ（セキュリティ・監査重視）

```yaml
harness:
  agent_loop:
    max_iterations: 50
    timeout_seconds: 300
    enable_audit_log: true
    
middleware:
  stack:
    - security     # 必須
    - context
    - memory
    - tools
    - monitoring
    - audit        # 監査ログ
    
security:
  pii_detection: true
  access_control: "strict"
  audit_level: "detailed"
```

### OSS プロジェクト（コミュニティ重視）

```yaml
project:
  type: "open-source"
  
skills:
  enable:
    - code_review
    - commit_message
    - contribution_guide
    
  custom:
    - name: "license_check"
      description: "ライセンス互換性チェック"
    - name: "community_standards"
      description: "コミュニティ標準準拠チェック"
```

## 🛠️ 開発環境別設定

### 開発環境

```yaml
environment: "development"

harness:
  agent_loop:
    enable_debug: true
    log_level: "DEBUG"
    enable_self_verification: false  # 高速化
    
monitoring:
  enable_detailed_logs: true
  performance_tracking: false
```

### ステージング環境

```yaml
environment: "staging"

harness:
  agent_loop:
    enable_debug: false
    log_level: "INFO"
    enable_self_verification: true
    
monitoring:
  enable_detailed_logs: true
  performance_tracking: true
  alert_thresholds:
    response_time_ms: 2000
```

### 本番環境

```yaml
environment: "production"

harness:
  agent_loop:
    enable_debug: false
    log_level: "WARN"
    enable_self_verification: true
    enable_circuit_breaker: true
    
security:
  strict_mode: true
  pii_redaction: true
  access_logging: "detailed"
  
monitoring:
  enable_metrics: true
  enable_alerting: true
  alert_thresholds:
    response_time_ms: 1000
    error_rate_percent: 1
```

## 🎨 カスタムスキル例

### TypeScript プロジェクト用

```python
# .ai-guidance/skills/typescript_review.py
@skill(
    name="typescript_review",
    description="TypeScript コードの型安全性とベストプラクティスチェック",
    triggers=["TypeScript", "型", "interface"],
    file_patterns=["*.ts", "*.tsx"]
)
class TypeScriptReviewSkill(Skill):
    async def execute(self, files):
        # TypeScript 固有のレビューロジック
        pass
```

### Docker プロジェクト用

```yaml
# .ai-guidance/skills/docker_review.yaml
name: "docker_review"
description: "Dockerfile と Docker Compose の最適化チェック"
triggers:
  - "Docker"
  - "コンテナ"
  - "Dockerfile"
file_patterns:
  - "Dockerfile*"
  - "docker-compose*.yml"
  - ".dockerignore"

rules:
  - check: "multi_stage_build"
    description: "マルチステージビルドの使用を推奨"
  - check: "security_scan"
    description: "脆弱性のあるベースイメージをチェック"
```

## 🔧 ミドルウェア設定例

### 高パフォーマンス設定

```yaml
middleware:
  performance:
    enable_caching: true
    cache_ttl_seconds: 3600
    enable_parallel_execution: true
    max_concurrent_tools: 5
    
  context:
    max_context_tokens: 8000
    enable_smart_truncation: true
    priority_preservation: ["recent", "important"]
```

### 高セキュリティ設定

```yaml
middleware:
  security:
    pii_patterns:
      - "credit_card"
      - "ssn"
      - "email"
      - "phone_number"
      - "custom_patterns": ["内部ID: [A-Z0-9]+"]
    
    access_control:
      require_authentication: true
      allowed_operations: ["read", "analyze"]
      restricted_operations: ["file_write", "system_command"]
```

これらの設定例を参考に、プロジェクトの要件に合わせてカスタマイズしてください。