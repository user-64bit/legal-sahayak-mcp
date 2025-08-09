# Legal Sahayak - Indian Legal Assistant MCP Server

[![Legal Sahayak](https://img.shields.io/badge/Legal%20Sahayak-Indian%20Legal%20Assistant-blue)](https://github.com/yourusername/legal-sahayak)
[![Puch AI Compatible](https://img.shields.io/badge/Puch%20AI-Compatible-green)](https://puch.ai)
[![MCP Protocol](https://img.shields.io/badge/MCP-Protocol-orange)](https://puch.ai/mcp)

**Legal Sahayak** (Legal Helper) is a specialized MCP (Model Context Protocol) server that provides comprehensive legal assistance for Indian law matters. Whether you're dealing with employment bonds, POSH Act issues, consumer rights, or need legal document analysis, Legal Sahayak has you covered.

## 🏛️ What is Legal Sahayak?

Legal Sahayak is an AI-powered legal assistant specifically designed for the Indian legal system. It provides:

- **Expert guidance** on Indian laws and regulations
- **Document analysis** for contracts, agreements, and legal documents
- **Legal precedent research** from Indian courts
- **Immediate answers** to common legal questions
- **Step-by-step guidance** for legal procedures

## ⚖️ Legal Areas Covered

### 📋 Employment Law
- **Employment Bonds**: Consequences of breaking, legal defenses, validity under Indian Contract Act
- **POSH Act 2013**: Rights for accused/victims, complaint procedures, employer duties
- **Labour Law Compliance**: Industrial Disputes Act, wage laws, termination procedures
- **Non-compete Agreements**: Validity, enforceability, restraint of trade doctrine

### 📜 Contract Law
- **Indian Contract Act 1872**: Validity, consideration, breach remedies
- **Agreement Analysis**: Identifying unfair terms, legal compliance
- **Property Agreements**: Lease deeds, sale agreements, registration requirements
- **NDA & Confidentiality**: Duration clauses, return of materials

### 🛒 Consumer Rights
- **Consumer Protection Act 2019**: Rights, remedies, complaint procedures
- **Defective Products**: Replacement, refund, compensation claims
- **Service Deficiencies**: Banking, telecom, e-commerce disputes
- **Unfair Trade Practices**: Identification and legal recourse

### 🏠 Property Law
- **Registration Requirements**: Document registration, stamp duty
- **Landlord-Tenant Disputes**: Rent control, eviction procedures
- **Property Purchase**: Due diligence, title verification
- **Maintenance Issues**: Responsibility allocation, legal remedies

## 🚀 Quick Start Guide

### Step 1: Install Dependencies

Ensure you have Python 3.11+ installed:

```bash
# Create virtual environment
uv venv

# Install all required packages
uv sync

# Activate the environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

### Step 2: Configure Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
AUTH_TOKEN=your_secret_token_here
MY_NUMBER=919876543210
```

**Configuration Notes:**
- `AUTH_TOKEN`: Your secure authentication token (keep this secret!)
- `MY_NUMBER`: Your WhatsApp number in format `{country_code}{number}`

### Step 3: Launch Legal Sahayak Server

```bash
cd mcp-bearer-token
python mcp_starter.py
```

You'll see:
```
🔥 [LEGAL-SAHAYAK-MCP] ⚖️ Starting Legal Sahayak MCP Server - Indian Legal Assistant
🚀 Server running on http://0.0.0.0:8086
📚 Available tools: legal_consultation, legal_document_analyzer, indian_legal_search, legal_precedent_search
🔥 All responses will be prefixed with [LEGAL-SAHAYAK-MCP] for identification
```

### Step 4: Make Server Publicly Accessible

Since Puch AI requires HTTPS access, expose your local server:

#### Option A: Using ngrok (Recommended)

1. **Install ngrok**: Download from https://ngrok.com/download
2. **Get authtoken**: Visit https://dashboard.ngrok.com/get-started/your-authtoken
3. **Configure ngrok**: `ngrok config add-authtoken YOUR_AUTHTOKEN`
4. **Start tunnel**: `ngrok http 8086`

#### Option B: Cloud Deployment

Deploy to cloud platforms:
- **Railway**: Easy one-click deployment
- **Render**: Free tier available
- **Heroku**: Classic platform
- **DigitalOcean App Platform**: Reliable hosting

## 🔗 Connect with Puch AI

1. **Open Puch AI**: [Start conversation](https://wa.me/+919998881729)
2. **Connect your server**:
   ```
   /mcp connect https://your-domain.ngrok.app/mcp your_secret_token_here
   ```
3. **Enable debug mode** (optional):
   ```
   /mcp diagnostics-level debug
   ```

## 🛠️ Available Tools

### 1. 🔍 Legal Consultation (`legal_consultation`)
Get expert guidance on Indian legal matters.

**Example Usage:**
- *"What happens if I break my employment bond?"*
- *"I got accused under POSH act, what are my rights?"*
- *"Can my employer terminate me without notice?"*

**Features:**
- Covers employment bonds, POSH Act, consumer rights
- Provides potential consequences and legal defenses
- Includes relevant Indian laws and precedents
- Urgency level handling for immediate legal matters

### 2. 📋 Legal Document Analyzer (`legal_document_analyzer`)
Analyze contracts, agreements, and legal documents for potential issues.

**Example Usage:**
- Upload employment contracts for analysis
- Review lease agreements for unfair terms
- Check NDAs for compliance issues
- Analyze property sale deeds

**Features:**
- Identifies red flags and areas of concern
- Indian law compliance checking
- Actionable recommendations
- Support for URLs and direct text input

### 3. 🔍 Indian Legal Search (`indian_legal_search`)
Search for specific Indian laws, acts, amendments, and legal provisions.

**Example Usage:**
- *"Find recent amendments to Consumer Protection Act"*
- *"Search for Indian Contract Act Section 73"*
- *"Look up POSH Act guidelines"*

**Features:**
- Targets official government sources (indiacode.nic.in, sci.gov.in)
- Categorizes results by source type
- Filters by jurisdiction and search type
- Provides guidance on using legal resources

### 4. 📚 Legal Precedent Search (`legal_precedent_search`)
Find relevant case law and court judgments from Indian courts.

**Example Usage:**
- *"Find precedents on employment bond validity"*
- *"Search Supreme Court judgments on POSH Act"*
- *"Look for High Court rulings on consumer disputes"*

**Features:**
- Searches Supreme Court, High Court, and District Court judgments
- Explains binding vs. persuasive precedents
- Provides guidance on using case law
- Time-based filtering (recent, decade, all-time)

## 📖 Example Legal Queries

### Employment Bond Issues
```
Query: "My company wants me to pay ₹2 lakhs if I leave before 2 years. Is this legal?"

Response: 🔥 [LEGAL-SAHAYAK-MCP] ⚖️ Legal Sahayak - Indian Legal Consultation

📋 Employment Bond Analysis:
What it means: Employment bonds are agreements where employees commit to work for a specified period

Potential consequences of breaking:
• Potential monetary penalty as specified in the bond
• Legal action for breach of contract
• Recovery of training costs and other expenses
• Possible impact on future employment references

Possible legal defenses:
• Unreasonable restraint of trade (if bond terms are excessive)
• Lack of consideration (if no benefits provided during training)
• Unconscionable terms (if penalty is disproportionate)
• Misrepresentation or fraud in bond execution

Relevant Laws: Indian Contract Act 1872, Industrial Disputes Act 1947
```

### POSH Act Guidance
```
Query: "I've been accused of workplace harassment. What should I do?"

Response: 🔥 [LEGAL-SAHAYAK-MCP] ⚖️ Legal Sahayak - Indian Legal Consultation

🛡️ POSH Act Analysis:
About POSH Act: Prevention of Sexual Harassment (POSH) Act 2013 protects women at workplace

Your rights if accused:
• Right to fair hearing and due process
• Right to legal representation
• Presumption of innocence until proven guilty
• Protection against false/malicious complaints
• Right to cross-examine witnesses

Relevant Laws: Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013
```

## 🎯 Identifying MCP Responses

All responses from Legal Sahayak are prefixed with `🔥 **[LEGAL-SAHAYAK-MCP]**` so you can easily distinguish between:

- **Legal Sahayak MCP responses**: Always start with `🔥 [LEGAL-SAHAYAK-MCP]`
- **Direct Puch AI responses**: No special prefix

## ⚠️ Important Legal Disclaimers

1. **Educational Purpose Only**: All information provided is for educational purposes and general guidance
2. **Not Legal Advice**: This does not constitute formal legal advice
3. **Consult Professionals**: Always consult qualified legal practitioners for specific legal matters
4. **No Attorney-Client Privilege**: Communications are not protected by attorney-client privilege
5. **Jurisdiction Specific**: Guidance is specific to Indian law and may not apply elsewhere

## 🛠️ Customization Guide

### Adding New Legal Areas

1. **Update knowledge base** in `legal_consultation` tool:
```python
legal_knowledge_base = {
    "your_new_area": {
        "description": "Area description",
        "key_points": ["Point 1", "Point 2"],
        "relevant_laws": ["Act Name Year"]
    }
}
```

2. **Add query detection logic**:
```python
elif any(term in query_lower for term in ["new_area_keywords"]):
    # Handle new area logic
```

### Extending Document Analysis

Add new document type analysis in `legal_document_analyzer`:

```python
# New document type analysis
if any(term in content_lower for term in ["new_doc_type"]):
    if "specific_clause" in content_lower:
        red_flags.append("Specific issue description")
```

## 📚 Legal Resources

### Official Government Sources
- **India Code**: https://www.indiacode.nic.in/ (Official legal database)
- **Supreme Court of India**: https://main.sci.gov.in/
- **Ministry of Law & Justice**: https://lawmin.gov.in/
- **Legislative Department**: https://legislative.gov.in/

### Case Law Databases
- **Indian Kanoon**: https://indiankanoon.org/ (Free case law)
- **SCC Online**: https://www.scconline.com/ (Subscription)
- **Manupatra**: https://www.manupatra.com/ (Subscription)

### Legal Help Resources
- **National Legal Services Authority**: https://nalsa.gov.in/
- **Lok Adalat Services**: For alternative dispute resolution
- **Legal Aid Clinics**: State-wise legal aid services

## 🆘 Getting Help & Support

### Puch AI Community
- **Discord Server**: https://discord.gg/VMCnMvYx
- **Official Documentation**: https://puch.ai/mcp
- **WhatsApp Support**: +91 99988 81729

### Legal Sahayak Issues
- **Technical Issues**: Check server logs and MCP connection
- **Legal Content**: Verify against official legal sources
- **Feature Requests**: Contact through Puch AI community

### Troubleshooting

**Common Issues:**

1. **Server not responding**: Check if port 8086 is accessible
2. **Authentication errors**: Verify AUTH_TOKEN in .env file
3. **Legal information outdated**: Cross-reference with official sources
4. **MCP connection failed**: Ensure HTTPS tunnel is active

## 🚀 Deployment Options

### Production Deployment

For production use, consider:

1. **Environment Security**: Use environment variable injection
2. **HTTPS Certificate**: Obtain valid SSL certificate
3. **Load Balancing**: For high-traffic scenarios
4. **Database Integration**: For storing user queries and responses
5. **Logging**: Implement comprehensive logging for debugging

### Performance Optimization

- **Caching**: Cache frequently accessed legal information
- **Rate Limiting**: Implement rate limiting for API calls
- **Response Time**: Optimize database queries and external API calls

## 📄 License & Terms

This project is designed for educational and informational purposes. Users are responsible for:

- **Compliance**: Ensuring compliance with local laws and regulations
- **Professional Consultation**: Seeking qualified legal advice for serious matters
- **Data Privacy**: Protecting sensitive legal information
- **Ethical Use**: Using the tool responsibly and ethically

---

## 🎉 Ready to Use Legal Sahayak?

1. **Set up** the server following the Quick Start Guide
2. **Connect** with Puch AI using your server URL
3. **Start asking** legal questions and get expert guidance
4. **Remember** to consult qualified lawyers for serious legal matters

**Use hashtag `#LegalSahayak` and `#BuildWithPuch` when sharing your legal tech innovations!**

**Legal Sahayak - Your trusted companion for navigating Indian law! ⚖️🇮🇳**