import asyncio
from typing import Annotated
import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
from mcp import ErrorData, McpError
from mcp.server.auth.provider import AccessToken
from mcp.types import TextContent, ImageContent, INVALID_PARAMS, INTERNAL_ERROR
from pydantic import BaseModel, Field, AnyUrl

import markdownify
import httpx
import readabilipy

# --- Load environment variables ---
load_dotenv()

TOKEN = os.environ.get("AUTH_TOKEN")
MY_NUMBER = os.environ.get("MY_NUMBER")

assert TOKEN is not None, "Please set AUTH_TOKEN in your .env file"
assert MY_NUMBER is not None, "Please set MY_NUMBER in your .env file"

# --- Auth Provider ---
class SimpleBearerAuthProvider(BearerAuthProvider):
    def __init__(self, token: str):
        k = RSAKeyPair.generate()
        super().__init__(public_key=k.public_key, jwks_uri=None, issuer=None, audience=None)
        self.token = token

    async def load_access_token(self, token: str) -> AccessToken | None:
        if token == self.token:
            return AccessToken(
                token=token,
                client_id="puch-client",
                scopes=["*"],
                expires_at=None,
            )
        return None

# --- Rich Tool Description model ---
class RichToolDescription(BaseModel):
    description: str
    use_when: str
    side_effects: str | None = None

# --- Fetch Utility Class ---
class Fetch:
    USER_AGENT = "Puch/1.0 (Autonomous)"

    @classmethod
    async def fetch_url(
        cls,
        url: str,
        user_agent: str,
        force_raw: bool = False,
    ) -> tuple[str, str]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    follow_redirects=True,
                    headers={"User-Agent": user_agent},
                    timeout=30,
                )
            except httpx.HTTPError as e:
                raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Failed to fetch {url}: {e!r}"))

            if response.status_code >= 400:
                raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Failed to fetch {url} - status code {response.status_code}"))

            page_raw = response.text

        content_type = response.headers.get("content-type", "")
        is_page_html = "text/html" in content_type

        if is_page_html and not force_raw:
            return cls.extract_content_from_html(page_raw), ""

        return (
            page_raw,
            f"Content type {content_type} cannot be simplified to markdown, but here is the raw content:\n",
        )

    @staticmethod
    def extract_content_from_html(html: str) -> str:
        """Extract and convert HTML content to Markdown format."""
        ret = readabilipy.simple_json.simple_json_from_html_string(html, use_readability=True)
        if not ret or not ret.get("content"):
            return "<error>Page failed to be simplified from HTML</error>"
        content = markdownify.markdownify(ret["content"], heading_style=markdownify.ATX)
        return content

    @staticmethod
    async def google_search_links(query: str, num_results: int = 5) -> list[str]:
        """
        Perform a scoped DuckDuckGo search and return a list of job posting URLs.
        (Using DuckDuckGo because Google blocks most programmatic scraping.)
        """
        ddg_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
        links = []

        async with httpx.AsyncClient() as client:
            resp = await client.get(ddg_url, headers={"User-Agent": Fetch.USER_AGENT})
            if resp.status_code != 200:
                return ["<error>Failed to perform search.</error>"]

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", class_="result__a", href=True):
            href = a["href"]
            if "http" in href:
                links.append(href)
            if len(links) >= num_results:
                break

        return links or ["<error>No results found.</error>"]

# --- MCP Server Setup ---
mcp = FastMCP(
    "Legal Sahayak MCP Server - Indian Legal Assistant",
    auth=SimpleBearerAuthProvider(TOKEN),
)

# --- Tool: validate (required by Puch) ---
@mcp.tool
async def validate() -> str:
    return f"🔥 [LEGAL-SAHAYAK-MCP] Validation: {MY_NUMBER}"

# --- Tool: legal_consultation ---
LegalConsultationDescription = RichToolDescription(
    description="Provides legal guidance and consultation for Indian law matters including employment bonds, POSH act, contracts, property disputes, criminal law, family law, and other legal issues.",
    use_when="Use this when users ask about legal issues, consequences of actions, rights and obligations under Indian law, or need clarification on legal matters.",
    side_effects="Returns detailed legal information, potential consequences, suggested actions, and relevant legal provisions.",
)

@mcp.tool(description=LegalConsultationDescription.model_dump_json())
async def legal_consultation(
    legal_query: Annotated[str, Field(description="The user's legal question or situation description")],
    legal_area: Annotated[str | None, Field(description="Specific area of law (e.g., employment, criminal, family, property, consumer rights, POSH, contracts)")] = None,
    document_text: Annotated[str | None, Field(description="Text of any legal document to analyze (contract, bond, agreement, etc.)")] = None,
    urgency_level: Annotated[str, Field(description="Urgency level: immediate, moderate, or general_inquiry")] = "general_inquiry",
) -> str:
    """
    Provides comprehensive legal consultation for Indian law matters.
    """
    
    # Common Indian legal scenarios and responses
    legal_knowledge_base = {
        "employment_bond": {
            "description": "Employment bonds are agreements where employees commit to work for a specified period",
            "breaking_consequences": [
                "Potential monetary penalty as specified in the bond",
                "Legal action for breach of contract", 
                "Recovery of training costs and other expenses",
                "Possible impact on future employment references"
            ],
            "defenses": [
                "Unreasonable restraint of trade (if bond terms are excessive)",
                "Lack of consideration (if no benefits provided during training)",
                "Unconscionable terms (if penalty is disproportionate)",
                "Misrepresentation or fraud in bond execution"
            ],
            "relevant_laws": ["Indian Contract Act 1872", "Industrial Disputes Act 1947"]
        },
        "posh_act": {
            "description": "Prevention of Sexual Harassment (POSH) Act 2013 protects women at workplace",
            "if_accused": [
                "Right to fair hearing and due process",
                "Right to legal representation",
                "Presumption of innocence until proven guilty",
                "Protection against false/malicious complaints",
                "Right to cross-examine witnesses"
            ],
            "if_victim": [
                "Right to file complaint with Internal Committee (IC) or Local Committee (LC)",
                "Right to interim relief during inquiry",
                "Right to confidentiality and privacy",
                "Protection against victimization",
                "Right to compensation if harassment is proved"
            ],
            "employer_duties": [
                "Constitute Internal Committee",
                "Conduct fair and time-bound inquiry",
                "Provide safe working environment",
                "Take action based on IC recommendations"
            ],
            "relevant_laws": ["Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013"]
        },
        "consumer_rights": {
            "description": "Consumer Protection Act 2019 provides comprehensive protection to consumers",
            "rights": [
                "Right to safety from hazardous goods/services",
                "Right to be informed about quality, quantity, price",
                "Right to choose from variety of goods/services",
                "Right to be heard in consumer forums",
                "Right to seek redressal against unfair trade practices",
                "Right to consumer education"
            ],
            "remedies": [
                "Replacement or repair of defective goods",
                "Refund of amount paid",
                "Compensation for loss/injury",
                "Discontinuation of unfair trade practice"
            ],
            "relevant_laws": ["Consumer Protection Act 2019"]
        }
    }
    
    response = f"🔥 **[LEGAL-SAHAYAK-MCP]** ⚖️ **Legal Sahayak - Indian Legal Consultation**\n\n"
    response += f"**Query:** {legal_query}\n\n"
    
    if legal_area:
        response += f"**Legal Area:** {legal_area.title()}\n\n"
    
    if urgency_level == "immediate":
        response += "🚨 **URGENT LEGAL MATTER** - Consider consulting a qualified lawyer immediately.\n\n"
    
    # Analyze the query for specific legal scenarios
    query_lower = legal_query.lower()
    
    if any(term in query_lower for term in ["employment bond", "bond", "bond break", "training bond"]):
        bond_info = legal_knowledge_base["employment_bond"]
        response += f"📋 **Employment Bond Analysis:**\n\n"
        response += f"**What it means:** {bond_info['description']}\n\n"
        response += f"**Potential consequences of breaking:**\n"
        for consequence in bond_info["breaking_consequences"]:
            response += f"• {consequence}\n"
        response += f"\n**Possible legal defenses:**\n"
        for defense in bond_info["defenses"]:
            response += f"• {defense}\n"
        response += f"\n**Relevant Laws:** {', '.join(bond_info['relevant_laws'])}\n\n"
        
    elif any(term in query_lower for term in ["posh", "sexual harassment", "workplace harassment"]):
        posh_info = legal_knowledge_base["posh_act"]
        response += f"🛡️ **POSH Act Analysis:**\n\n"
        response += f"**About POSH Act:** {posh_info['description']}\n\n"
        
        if "accused" in query_lower:
            response += f"**Your rights if accused:**\n"
            for right in posh_info["if_accused"]:
                response += f"• {right}\n"
        elif "victim" in query_lower or "complaint" in query_lower:
            response += f"**Your rights as a victim:**\n"
            for right in posh_info["if_victim"]:
                response += f"• {right}\n"
        else:
            response += f"**General POSH Act provisions:**\n"
            response += f"**If you're accused:**\n"
            for right in posh_info["if_accused"]:
                response += f"• {right}\n"
            response += f"\n**If you're a victim:**\n"
            for right in posh_info["if_victim"]:
                response += f"• {right}\n"
        
        response += f"\n**Relevant Laws:** {', '.join(posh_info['relevant_laws'])}\n\n"
    
    elif any(term in query_lower for term in ["consumer", "defective product", "refund", "warranty"]):
        consumer_info = legal_knowledge_base["consumer_rights"]
        response += f"🛒 **Consumer Rights Analysis:**\n\n"
        response += f"**Consumer Protection:** {consumer_info['description']}\n\n"
        response += f"**Your rights as a consumer:**\n"
        for right in consumer_info["rights"]:
            response += f"• {right}\n"
        response += f"\n**Available remedies:**\n"
        for remedy in consumer_info["remedies"]:
            response += f"• {remedy}\n"
        response += f"\n**Relevant Laws:** {', '.join(consumer_info['relevant_laws'])}\n\n"
    
    # Document analysis if provided
    if document_text:
        response += f"📄 **Document Analysis:**\n\n"
        response += f"```\n{document_text.strip()[:500]}{'...' if len(document_text) > 500 else ''}\n```\n\n"
        response += f"**Key points to review:**\n"
        response += f"• Check for unreasonable terms and conditions\n"
        response += f"• Verify penalty clauses are proportionate\n"
        response += f"• Ensure terms comply with Indian law\n"
        response += f"• Look for any unconscionable provisions\n"
        response += f"• Check if adequate consideration is provided\n\n"
    
    # General legal advice
    response += f"💡 **General Recommendations:**\n"
    response += f"• This is general legal information, not specific legal advice\n"
    response += f"• Consult a qualified lawyer for your specific situation\n"
    response += f"• Keep all relevant documents and communications\n"
    response += f"• Know your rights under Indian law\n"
    response += f"• Consider alternative dispute resolution methods\n\n"
    
    response += f"⚠️ **Disclaimer:** This information is for educational purposes only and does not constitute legal advice. Please consult a qualified legal practitioner for specific legal guidance.\n"
    
    return response


# --- Tool: legal_document_analyzer ---
LegalDocumentAnalyzerDescription = RichToolDescription(
    description="Analyzes legal documents like employment contracts, bonds, agreements, property deeds, and other legal texts for potential issues under Indian law.",
    use_when="Use this when users provide legal documents or contracts for analysis, review, or interpretation.",
    side_effects="Returns detailed analysis of document clauses, identifies potential legal issues, and suggests areas of concern.",
)

@mcp.tool(description=LegalDocumentAnalyzerDescription.model_dump_json())
async def legal_document_analyzer(
    document_content: Annotated[str, Field(description="Full text content of the legal document to analyze")],
    document_type: Annotated[str | None, Field(description="Type of document (e.g., employment contract, bond, lease agreement, property deed, NDA)")] = None,
    specific_concerns: Annotated[str | None, Field(description="Specific areas of concern or questions about the document")] = None,
    document_url: Annotated[AnyUrl | None, Field(description="URL to fetch document from if not provided as text")] = None,
) -> str:
    """
    Provides detailed analysis of legal documents under Indian law.
    """
    
    # If URL is provided, fetch the document
    if document_url and not document_content:
        content, _ = await Fetch.fetch_url(str(document_url), Fetch.USER_AGENT)
        document_content = content
    
    if not document_content or len(document_content.strip()) < 50:
        raise McpError(ErrorData(code=INVALID_PARAMS, message="Please provide document content with at least 50 characters for meaningful analysis."))
    
    response = f"🔥 **[LEGAL-SAHAYAK-MCP]** 📋 **Legal Document Analysis - Legal Sahayak**\n\n"
    
    if document_type:
        response += f"**Document Type:** {document_type.title()}\n\n"
    
    if specific_concerns:
        response += f"**Specific Concerns:** {specific_concerns}\n\n"
    
    # Document preview
    preview_length = 300
    response += f"**Document Preview:**\n```\n{document_content[:preview_length]}{'...' if len(document_content) > preview_length else ''}\n```\n\n"
    
    # Analyze document content for red flags
    content_lower = document_content.lower()
    red_flags = []
    yellow_flags = []
    
    # Employment bond specific analysis
    if any(term in content_lower for term in ["bond", "training", "service period", "employment"]):
        if "penalty" in content_lower or "damages" in content_lower:
            red_flags.append("Contains penalty clauses - verify if proportionate to actual losses")
        if "restraint" in content_lower or "non-compete" in content_lower:
            red_flags.append("Contains restraint of trade clauses - may be unenforceable if unreasonable")
        if "consideration" not in content_lower:
            yellow_flags.append("No clear mention of consideration - check if adequate benefits are provided")
    
    # Contract analysis
    if any(term in content_lower for term in ["contract", "agreement", "terms"]):
        if "jurisdiction" not in content_lower:
            yellow_flags.append("No jurisdiction clause mentioned - disputes may face forum issues")
        if "termination" not in content_lower:
            yellow_flags.append("No clear termination clause - check exit provisions")
        if "force majeure" not in content_lower:
            yellow_flags.append("No force majeure clause - may lack protection in unforeseen circumstances")
    
    # Property related
    if any(term in content_lower for term in ["property", "lease", "rent", "premises"]):
        if "registration" not in content_lower and "lease" in content_lower:
            red_flags.append("Lease agreement may require registration if rent exceeds ₹100 per month")
        if "maintenance" not in content_lower:
            yellow_flags.append("Maintenance responsibilities not clearly defined")
    
    # NDA/Confidentiality
    if any(term in content_lower for term in ["confidential", "non-disclosure", "proprietary"]):
        if "duration" not in content_lower:
            yellow_flags.append("No clear duration for confidentiality obligations")
        if "return of materials" not in content_lower:
            yellow_flags.append("No clause for return of confidential materials")
    
    # Display analysis results
    if red_flags:
        response += f"🚨 **Critical Issues Found:**\n"
        for flag in red_flags:
            response += f"• {flag}\n"
        response += "\n"
    
    if yellow_flags:
        response += f"⚠️ **Areas of Concern:**\n"
        for flag in yellow_flags:
            response += f"• {flag}\n"
        response += "\n"
    
    # General analysis points
    response += f"🔍 **General Document Analysis:**\n\n"
    
    response += f"**Key Clauses to Review:**\n"
    response += f"• Payment/Compensation terms and timelines\n"
    response += f"• Termination conditions and notice periods\n"
    response += f"• Dispute resolution mechanism\n"
    response += f"• Governing law and jurisdiction\n"
    response += f"• Force majeure provisions\n"
    response += f"• Indemnity and liability clauses\n\n"
    
    response += f"**Indian Law Compliance Check:**\n"
    response += f"• Ensure terms don't violate fundamental rights\n"
    response += f"• Check compliance with relevant labour laws\n"
    response += f"• Verify penalty clauses are reasonable and not penal\n"
    response += f"• Confirm consideration is adequate and legal\n"
    response += f"• Review for any unconscionable terms\n\n"
    
    response += f"**Recommended Actions:**\n"
    response += f"• Get the document reviewed by a qualified lawyer\n"
    response += f"• Negotiate unfavorable terms before signing\n"
    response += f"• Keep copies of all versions and amendments\n"
    response += f"• Understand all implications before execution\n"
    response += f"• Consider legal insurance if available\n\n"
    
    if specific_concerns:
        response += f"**Regarding Your Specific Concerns:**\n"
        response += f"Based on '{specific_concerns}', pay special attention to related clauses and seek specific legal advice on this matter.\n\n"
    
    response += f"⚠️ **Disclaimer:** This analysis is for informational purposes only. Please consult a qualified legal practitioner for specific legal advice regarding this document.\n"
    
    return response


# --- Tool: indian_legal_search ---
IndianLegalSearchDescription = RichToolDescription(
    description="Searches for information about Indian laws, acts, rules, amendments, and legal provisions using web search.",
    use_when="Use this to find specific information about Indian legal statutes, recent amendments, court judgments, or legal precedents.",
    side_effects="Returns search results with links to legal information sources, government websites, and legal databases.",
)

@mcp.tool(description=IndianLegalSearchDescription.model_dump_json())
async def indian_legal_search(
    search_query: Annotated[str, Field(description="Legal search query (e.g., 'Indian Contract Act 1872', 'POSH Act amendments', 'Supreme Court judgment on employment bonds')")],
    search_type: Annotated[str, Field(description="Type of search: acts, judgments, amendments, or general")] = "general",
    jurisdiction: Annotated[str, Field(description="Jurisdiction: supreme_court, high_court, district_court, or all")] = "all",
) -> str:
    """
    Searches for Indian legal information and provides relevant links and summaries.
    """
    
    # Enhance search query for Indian legal context
    enhanced_query = f"{search_query} Indian law"
    
    if search_type == "acts":
        enhanced_query += " act statute legislation India"
    elif search_type == "judgments":
        enhanced_query += " court judgment ruling India"
    elif search_type == "amendments":
        enhanced_query += " amendment modification India"
    
    if jurisdiction != "all":
        enhanced_query += f" {jurisdiction.replace('_', ' ')}"
    
    # Add Indian legal site preferences
    enhanced_query += " site:indiacode.nic.in OR site:sci.gov.in OR site:lawmin.gov.in OR site:advocatekhoj.com OR site:manupatra.com"
    
    # Perform search
    links = await Fetch.google_search_links(enhanced_query, num_results=8)
    
    response = f"🔥 **[LEGAL-SAHAYAK-MCP]** 🔍 **Indian Legal Search Results**\n\n"
    response += f"**Search Query:** {search_query}\n"
    response += f"**Search Type:** {search_type.title()}\n"
    response += f"**Jurisdiction:** {jurisdiction.replace('_', ' ').title()}\n\n"
    
    if links and links[0] != "<error>No results found.</error>":
        response += f"**Relevant Legal Resources:**\n\n"
        
        for i, link in enumerate(links, 1):
            if "error" not in link.lower():
                # Categorize links based on domain
                if "indiacode.nic.in" in link:
                    response += f"{i}. 📜 **Official Legislation:** {link}\n"
                elif "sci.gov.in" in link:
                    response += f"{i}. ⚖️ **Supreme Court:** {link}\n"
                elif "lawmin.gov.in" in link:
                    response += f"{i}. 🏛️ **Ministry of Law:** {link}\n"
                elif any(site in link for site in ["advocatekhoj.com", "manupatra.com", "scconline.com"]):
                    response += f"{i}. 📚 **Legal Database:** {link}\n"
                else:
                    response += f"{i}. 🔗 **Legal Resource:** {link}\n"
        
        response += f"\n**How to Use These Resources:**\n"
        response += f"• Official government sites (.gov.in) provide authentic legal texts\n"
        response += f"• Legal databases offer case law and commentary\n"
        response += f"• Cross-reference information from multiple sources\n"
        response += f"• Look for recent amendments and updates\n"
        response += f"• Pay attention to court hierarchies and binding precedents\n\n"
        
    else:
        response += f"❌ **No specific results found.** Try:\n"
        response += f"• Refining your search terms\n"
        response += f"• Using official act names or section numbers\n"
        response += f"• Searching for broader legal concepts first\n"
        response += f"• Checking spelling of legal terms\n\n"
    
    response += f"💡 **Recommended Legal Resources:**\n"
    response += f"• **India Code:** https://www.indiacode.nic.in/ (Official legal database)\n"
    response += f"• **Supreme Court of India:** https://main.sci.gov.in/\n"
    response += f"• **Ministry of Law & Justice:** https://lawmin.gov.in/\n"
    response += f"• **Legislative Department:** https://legislative.gov.in/\n\n"
    
    response += f"⚠️ **Note:** Always verify legal information from official government sources and consult qualified legal practitioners for specific advice.\n"
    
    return response


# --- Tool: legal_precedent_search ---
LegalPrecedentSearchDescription = RichToolDescription(
    description="Searches for legal precedents, case law, and court judgments relevant to specific legal issues in Indian courts.",
    use_when="Use this to find relevant case law, court judgments, and legal precedents that might apply to a user's legal situation.",
    side_effects="Returns search results with links to court judgments, case summaries, and legal precedent information.",
)

@mcp.tool(description=LegalPrecedentSearchDescription.model_dump_json())
async def legal_precedent_search(
    case_facts: Annotated[str, Field(description="Brief description of the legal issue or facts for which precedents are needed")],
    legal_area: Annotated[str | None, Field(description="Area of law (employment, contract, criminal, family, property, etc.)")] = None,
    court_level: Annotated[str, Field(description="Court level: supreme_court, high_court, district_court, or all")] = "all",
    time_period: Annotated[str, Field(description="Time period: recent (5 years), decade (10 years), or all_time")] = "recent",
) -> str:
    """
    Searches for relevant legal precedents and case law for Indian legal matters.
    """
    
    # Build search query for case law
    search_terms = [case_facts]
    
    if legal_area:
        search_terms.append(legal_area)
    
    # Add court-specific terms
    if court_level == "supreme_court":
        search_terms.extend(["Supreme Court", "SC", "AIR", "SCC"])
    elif court_level == "high_court":
        search_terms.extend(["High Court", "HC"])
    elif court_level == "district_court":
        search_terms.extend(["District Court", "Sessions Court"])
    
    # Add Indian legal terms
    search_terms.extend(["India", "judgment", "ruling", "precedent", "case law"])
    
    # Time-based search enhancement
    if time_period == "recent":
        search_terms.append("2019..2024")
    elif time_period == "decade":
        search_terms.append("2014..2024")
    
    # Construct enhanced search query
    case_search_query = " ".join(search_terms)
    case_search_query += " site:sci.gov.in OR site:indiankanoon.org OR site:manupatra.com OR site:scconline.com"
    
    # Perform search
    links = await Fetch.google_search_links(case_search_query, num_results=10)
    
    response = f"🔥 **[LEGAL-SAHAYAK-MCP]** 📚 **Legal Precedent Search Results**\n\n"
    response += f"**Case Facts/Issue:** {case_facts}\n"
    
    if legal_area:
        response += f"**Legal Area:** {legal_area.title()}\n"
    
    response += f"**Court Level:** {court_level.replace('_', ' ').title()}\n"
    response += f"**Time Period:** {time_period.replace('_', ' ').title()}\n\n"
    
    if links and links[0] != "<error>No results found.</error>":
        response += f"**Relevant Case Law & Precedents:**\n\n"
        
        for i, link in enumerate(links, 1):
            if "error" not in link.lower():
                # Categorize links based on source
                if "sci.gov.in" in link:
                    response += f"{i}. ⚖️ **Supreme Court Judgment:** {link}\n"
                elif "indiankanoon.org" in link:
                    response += f"{i}. 📖 **Indian Kanoon (Case Database):** {link}\n"
                elif "manupatra.com" in link:
                    response += f"{i}. 📚 **Manupatra Legal Database:** {link}\n"
                elif "scconline.com" in link:
                    response += f"{i}. 🔍 **SCC Online:** {link}\n"
                elif any(hc in link.lower() for hc in ["hc", "high", "court"]):
                    response += f"{i}. 🏛️ **High Court Judgment:** {link}\n"
                else:
                    response += f"{i}. ⚖️ **Legal Precedent:** {link}\n"
        
        response += f"\n**How to Use These Precedents:**\n"
        response += f"• Read the full judgment to understand the ratio decidendi (legal reasoning)\n"
        response += f"• Check if the precedent is binding or persuasive for your case\n"
        response += f"• Supreme Court judgments are binding on all lower courts\n"
        response += f"• High Court judgments bind lower courts in the same state\n"
        response += f"• Look for similar facts and legal issues in the cases\n"
        response += f"• Note any subsequent amendments to relevant laws\n\n"
        
        response += f"**Understanding Legal Precedents:**\n"
        response += f"• **Ratio Decidendi:** The legal principle that forms the basis of the decision\n"
        response += f"• **Obiter Dicta:** Observations that are not binding but persuasive\n"
        response += f"• **Binding Precedent:** Must be followed by lower courts\n"
        response += f"• **Persuasive Precedent:** May be considered but not mandatory\n"
        response += f"• **Distinguishing:** Showing why a precedent doesn't apply to your case\n\n"
        
    else:
        response += f"❌ **No specific precedents found.** Try:\n"
        response += f"• Broadening your search terms\n"
        response += f"• Searching for the specific legal provision or section\n"
        response += f"• Looking for landmark cases in the legal area\n"
        response += f"• Consulting legal databases directly\n\n"
    
    # Add specific guidance based on legal area
    if legal_area:
        if legal_area.lower() in ["employment", "labour", "bond"]:
            response += f"**Key Employment Law Precedents to Consider:**\n"
            response += f"• Cases on validity of employment bonds\n"
            response += f"• Restraint of trade doctrine applications\n"
            response += f"• Industrial Disputes Act interpretations\n"
            response += f"• Labour law compliance requirements\n\n"
        elif legal_area.lower() in ["contract", "agreement"]:
            response += f"**Key Contract Law Precedents to Consider:**\n"
            response += f"• Indian Contract Act 1872 interpretations\n"
            response += f"• Breach of contract remedies\n"
            response += f"• Specific performance cases\n"
            response += f"• Unconscionable contract terms\n\n"
    
    response += f"💡 **Recommended Legal Databases:**\n"
    response += f"• **Indian Kanoon:** https://indiankanoon.org/ (Free case law database)\n"
    response += f"• **Supreme Court of India:** https://main.sci.gov.in/\n"
    response += f"• **SCC Online:** https://www.scconline.com/ (Subscription required)\n"
    response += f"• **Manupatra:** https://www.manupatra.com/ (Subscription required)\n\n"
    
    response += f"⚠️ **Important:** Legal precedents must be analyzed by qualified legal professionals. This search is for informational purposes only.\n"
    
    return response

# --- Run MCP Server ---
async def main():
    print("🔥 [LEGAL-SAHAYAK-MCP] ⚖️ Starting Legal Sahayak MCP Server - Indian Legal Assistant")
    print("🚀 Server running on http://0.0.0.0:8086")
    print("📚 Available tools: legal_consultation, legal_document_analyzer, indian_legal_search, legal_precedent_search")
    print("🔥 All responses will be prefixed with [LEGAL-SAHAYAK-MCP] for identification")
    await mcp.run_async("streamable-http", host="0.0.0.0", port=8086)

if __name__ == "__main__":
    asyncio.run(main())
