# PrecisionBOM Design Document

## Product Vision

PrecisionBOM streamlines electronic component sourcing by combining AI-powered analysis with blockchain-backed audit trails. Engineers upload a BOM, get intelligent part recommendations, and maintain a verifiable record of sourcing decisions.

## Core User Flows

### 1. BOM Upload and Processing

```
User uploads CSV/Excel BOM
         │
         ▼
Parse file → Extract part numbers, quantities, references
         │
         ▼
Enrich each part with supplier data (DigiKey, Mouser, Octopart)
         │
         ▼
AI analyzes BOM for:
  - Alternative parts
  - Pricing optimization
  - Supply chain risks
  - Compliance issues
         │
         ▼
Present results to user for review
```

### 2. Part Search

```
User enters search query (part number, description, specs)
         │
         ▼
Query multiple suppliers in parallel
         │
         ▼
Aggregate and deduplicate results
         │
         ▼
Rank by relevance, availability, price
         │
         ▼
Display with comparison view
```

### 3. AI-Assisted Sourcing

```
User requests suggestions for a part
         │
         ▼
OpenAI analyzes:
  - Original part specs
  - Available alternatives
  - Price/availability tradeoffs
         │
         ▼
Return ranked suggestions with reasoning
```

### 4. Blockchain Audit Trail

```
User finalizes sourcing decision
         │
         ▼
Generate JSON record of decision
         │
         ▼
Sign and submit to ERC-7827 contract
         │
         ▼
Record permanently stored with version history
```

## Data Models

### BOM Item

```typescript
interface BOMItem {
  lineNumber: number;
  partNumber: string;
  manufacturer: string;
  description: string;
  quantity: number;
  referenceDesignator: string;
  alternatives?: PartAlternative[];
  enrichedData?: EnrichedPartData;
}
```

### Enriched Part Data

```typescript
interface EnrichedPartData {
  supplier: string;
  supplierPartNumber: string;
  unitPrice: number;
  currency: string;
  stockQuantity: number;
  leadTimeDays: number;
  minOrderQuantity: number;
  datasheet?: string;
  lifecycle?: string;
  rohs?: boolean;
}
```

### Part Alternative

```typescript
interface PartAlternative {
  partNumber: string;
  manufacturer: string;
  similarity: number;  // 0-1 score
  reason: string;      // AI explanation
  priceComparison: number;  // % difference
}
```

### Audit Record (ERC-7827)

```json
{
  "bom_id": "BOM-2026-001",
  "decision_type": "part_substitution",
  "original_part": "LM7805CT",
  "selected_part": "L7805CV",
  "quantity": 100,
  "unit_price": "0.45",
  "total_cost": "45.00",
  "supplier": "DigiKey",
  "approved_by": "user@company.com",
  "timestamp": "2026-01-11T12:00:00Z",
  "reason": "Better availability, same specs"
}
```

## API Design

### REST Endpoints

#### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create new account |
| POST | `/api/auth/login` | Authenticate user |
| POST | `/api/auth/logout` | End session |
| POST | `/api/auth/forgot-password` | Request reset |
| POST | `/api/auth/reset-password` | Complete reset |

#### BOM Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/parse-bom` | Upload and parse BOM file |
| GET | `/api/search-parts` | Search parts by query |
| POST | `/api/suggest` | Get AI suggestions for part |
| POST | `/api/suggest-boms` | Get suggestions for entire BOM |

#### Blockchain

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/gatekeeper` | Write record to chain |
| GET | `/api/gatekeeper/:key` | Read record from chain |

### Request/Response Examples

#### Parse BOM

```bash
POST /api/parse-bom
Content-Type: multipart/form-data

file: <bom.csv>
```

```json
{
  "success": true,
  "items": [
    {
      "lineNumber": 1,
      "partNumber": "RC0805FR-0710KL",
      "manufacturer": "Yageo",
      "description": "RES 10K OHM 1% 1/8W 0805",
      "quantity": 100,
      "referenceDesignator": "R1-R100"
    }
  ]
}
```

#### Search Parts

```bash
GET /api/search-parts?q=STM32F103&limit=10
```

```json
{
  "results": [
    {
      "partNumber": "STM32F103C8T6",
      "manufacturer": "STMicroelectronics",
      "description": "MCU 32-bit ARM Cortex M3 64KB Flash",
      "suppliers": [
        {
          "name": "DigiKey",
          "price": 2.50,
          "stock": 5000,
          "leadTime": 0
        }
      ]
    }
  ]
}
```

## AI Agent Design

### Agent Specializations

#### Engineering Agent

**Focus**: Technical validation and compliance

**Evaluates**:
- Specification matching
- Form factor compatibility
- Environmental ratings (temperature, humidity)
- Compliance (RoHS, REACH, conflict minerals)
- Lifecycle status (active, NRND, obsolete)

**Output**: Technical risk score and recommendations

#### Sourcing Agent

**Focus**: Supply chain risk and availability

**Evaluates**:
- Current stock levels across distributors
- Lead times and trends
- Supplier reliability scores
- Geographic distribution of supply
- Historical availability

**Output**: Supply risk score and mitigation strategies

#### Finance Agent

**Focus**: Cost optimization

**Evaluates**:
- Unit pricing across quantities
- Volume discount opportunities
- Currency exposure
- Total cost of ownership
- Budget alignment

**Output**: Cost analysis and optimization recommendations

### Agent Orchestration

Using CrewAI's Flow system:

```python
class BOMReviewFlow(Flow):
    @start()
    def ingest(self):
        return self.parse_bom()

    @listen(ingest)
    def engineering_review(self, bom_data):
        return self.engineering_agent.execute(bom_data)

    @listen(engineering_review)
    def sourcing_review(self, eng_results):
        return self.sourcing_agent.execute(eng_results)

    @listen(sourcing_review)
    def finance_review(self, src_results):
        return self.finance_agent.execute(src_results)

    @listen(finance_review)
    def generate_report(self, fin_results):
        return self.compile_final_report(fin_results)
```

## Blockchain Integration

### ERC-7827 Usage

The contract stores sourcing decisions as JSON key-value pairs:

```
Key: "decision_2025_001"
Value: {"part": "LM7805", "action": "substitute", ...}
```

Version history allows auditing all changes:

```solidity
function version(string calldata key) returns (string[] memory)
// Returns: ["v1_json", "v2_json", "v3_json"]
```

### When to Record

1. **Part substitution approved** - Record original and substitute
2. **Supplier selection** - Record chosen supplier and alternatives
3. **Price negotiation** - Record agreed pricing
4. **Order placement** - Record final order details

### Privacy Considerations

- Only decision metadata stored on-chain
- Sensitive pricing can be hashed if needed
- User emails stored as hashes
- Full details remain in off-chain database

## Error Handling

### API Errors

```typescript
interface APIError {
  error: string;
  code: string;
  details?: Record<string, any>;
}
```

Common error codes:
- `AUTH_REQUIRED` - User must be authenticated
- `INVALID_INPUT` - Request validation failed
- `SUPPLIER_ERROR` - External API failure
- `RATE_LIMITED` - Too many requests
- `BLOCKCHAIN_ERROR` - Contract interaction failed

### Retry Strategy

| Error Type | Retry | Backoff |
|------------|-------|---------|
| Network timeout | Yes | Exponential |
| Rate limit | Yes | Wait for reset |
| Auth failure | No | - |
| Validation | No | - |

## Future Considerations

### Planned Features

1. **Multi-project support** - Manage multiple BOMs per user
2. **Team collaboration** - Shared BOMs with role-based access
3. **Automatic reordering** - Trigger orders at low stock
4. **Price alerts** - Notify on price changes
5. **BOM diff** - Compare BOM versions

### Technical Debt

- [ ] Add comprehensive test coverage
- [ ] Implement request caching layer
- [ ] Add WebSocket for real-time updates
- [ ] Migrate to edge runtime where possible
