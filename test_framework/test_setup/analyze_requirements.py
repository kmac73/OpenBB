#!/usr/bin/env python3
"""
OpenBB Test Framework Generator - Requirements Analyzer
Analyzes strategy requirement documents to extract test categories and requirements.
"""

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Any


class RequirementsAnalyzer:
    """Analyzes strategy requirements documents to extract testing information."""
    
    def __init__(self):
        self.analysis = {
            "framework_name": "",
            "strategy_type": "",
            "test_categories": {},
            "parameters": {},
            "trading_logic": {},
            "risk_management": {},
            "data_requirements": {},
            "ui_components": {},
            "integration_points": {},
            "performance_targets": {},
            "compliance_requirements": {}
        }
    
    def analyze_document(self, doc_path: Path, framework_name: str) -> Dict[str, Any]:
        """Main analysis function."""
        print(f"📄 Analyzing requirements document: {doc_path}")
        
        content = doc_path.read_text(encoding='utf-8')
        
        self.analysis["framework_name"] = framework_name
        self.analysis["strategy_type"] = self._extract_strategy_type(content)
        
        # Extract different components
        self._extract_parameters(content)
        self._extract_trading_logic(content)
        self._extract_risk_management(content)
        self._extract_data_requirements(content)
        self._extract_performance_targets(content)
        self._extract_compliance_requirements(content)
        
        # Generate test categories based on extracted information
        self._generate_test_categories()
        
        return self.analysis
    
    def _extract_strategy_type(self, content: str) -> str:
        """Extract strategy type from document."""
        # Look for common strategy patterns
        content_lower = content.lower()
        
        strategy_types = {
            "cfd": ["cfd", "contract for differences"],
            "momentum": ["momentum", "trend following"],
            "mean_reversion": ["mean reversion", "reversal"],
            "arbitrage": ["arbitrage", "pairs trading"],
            "scalping": ["scalping", "high frequency"],
            "swing": ["swing trading", "position trading"],
            "options": ["options", "derivatives"],
            "futures": ["futures", "commodities"],
            "forex": ["forex", "currency", "fx"],
            "crypto": ["crypto", "bitcoin", "ethereum"],
            "equity": ["equity", "stocks", "shares"]
        }
        
        for strategy_type, keywords in strategy_types.items():
            if any(keyword in content_lower for keyword in keywords):
                return strategy_type
        
        return "general"
    
    def _extract_parameters(self, content: str) -> None:
        """Extract strategy parameters from document."""
        parameters = {}
        
        # Look for parameter sections
        param_patterns = [
            r"(?i)##?\s*.*parameters.*\n(.*?)(?=\n##|\n#|$)",
            r"(?i)##?\s*.*settings.*\n(.*?)(?=\n##|\n#|$)",
            r"(?i)##?\s*.*configuration.*\n(.*?)(?=\n##|\n#|$)"
        ]
        
        for pattern in param_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                # Extract parameter definitions
                param_lines = re.findall(r"[-*]\s*\*\*(.*?)\*\*:?\s*(.*?)(?=\n|$)", match)
                for param_name, param_desc in param_lines:
                    parameters[param_name.strip()] = {
                        "description": param_desc.strip(),
                        "type": self._infer_parameter_type(param_desc)
                    }
        
        # Look for specific parameter values
        value_patterns = [
            r"(\w+):\s*\$?(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:%|pts?|points?)?",
            r"(\w+):\s*(\d+(?:\.\d+)?)\s*(?:%|pts?|points?|:1|x)",
        ]
        
        for pattern in value_patterns:
            matches = re.findall(pattern, content)
            for param_name, param_value in matches:
                if param_name.lower() in ['capital', 'risk', 'stop', 'target', 'threshold']:
                    if param_name not in parameters:
                        parameters[param_name] = {"description": "", "type": "numeric"}
                    parameters[param_name]["default_value"] = param_value
        
        self.analysis["parameters"] = parameters
    
    def _extract_trading_logic(self, content: str) -> None:
        """Extract trading logic requirements."""
        trading_logic = {
            "entry_conditions": [],
            "exit_conditions": [],
            "position_sizing": [],
            "session_management": [],
            "signal_generation": []
        }
        
        # Look for entry/exit conditions
        entry_patterns = [
            r"(?i)entry.*?conditions?:?\s*(.*?)(?=\n\n|\n#|exit|$)",
            r"(?i)long.*?entry:?\s*(.*?)(?=\n\n|\n#|short|$)",
            r"(?i)short.*?entry:?\s*(.*?)(?=\n\n|\n#|exit|$)"
        ]
        
        for pattern in entry_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                conditions = re.findall(r"[-*]\s*(.*?)(?=\n|$)", match)
                trading_logic["entry_conditions"].extend(conditions)
        
        # Look for exit conditions
        exit_patterns = [
            r"(?i)exit.*?conditions?:?\s*(.*?)(?=\n\n|\n#|$)",
            r"(?i)stop.*?loss:?\s*(.*?)(?=\n\n|\n#|$)",
            r"(?i)profit.*?target:?\s*(.*?)(?=\n\n|\n#|$)"
        ]
        
        for pattern in exit_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                conditions = re.findall(r"[-*]\s*(.*?)(?=\n|$)", match)
                trading_logic["exit_conditions"].extend(conditions)
        
        # Look for trading hours/session info
        session_patterns = [
            r"(?i)trading.*?hours?:?\s*(.*?)(?=\n\n|\n#|$)",
            r"(?i)session.*?management:?\s*(.*?)(?=\n\n|\n#|$)",
            r"(?i)active.*?hours?:?\s*(.*?)(?=\n\n|\n#|$)"
        ]
        
        for pattern in session_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                sessions = re.findall(r"[-*]\s*(.*?)(?=\n|$)", match)
                trading_logic["session_management"].extend(sessions)
        
        self.analysis["trading_logic"] = trading_logic
    
    def _extract_risk_management(self, content: str) -> None:
        """Extract risk management requirements."""
        risk_mgmt = {
            "position_limits": [],
            "drawdown_limits": [],
            "leverage_constraints": [],
            "risk_controls": []
        }
        
        # Look for risk management sections
        risk_patterns = [
            r"(?i)##?\s*.*risk.*management.*\n(.*?)(?=\n##|\n#|$)",
            r"(?i)##?\s*.*risk.*control.*\n(.*?)(?=\n##|\n#|$)"
        ]
        
        for pattern in risk_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                # Extract risk controls
                controls = re.findall(r"[-*]\s*(.*?)(?=\n|$)", match)
                risk_mgmt["risk_controls"].extend(controls)
        
        # Look for specific risk values
        if "leverage" in content.lower():
            leverage_matches = re.findall(r"(?i)(?:maximum|max)?\s*leverage:?\s*(\d+):1", content)
            risk_mgmt["leverage_constraints"] = leverage_matches
        
        if "drawdown" in content.lower():
            drawdown_matches = re.findall(r"(?i)(?:maximum|max)?\s*drawdown:?\s*(\d+)%", content)
            risk_mgmt["drawdown_limits"] = drawdown_matches
        
        self.analysis["risk_management"] = risk_mgmt
    
    def _extract_data_requirements(self, content: str) -> None:
        """Extract data requirements."""
        data_req = {
            "data_sources": [],
            "frequencies": [],
            "symbols": [],
            "date_ranges": []
        }
        
        # Extract frequencies
        freq_matches = re.findall(r"(\d+[MH]|1D|daily|intraday)", content)
        data_req["frequencies"] = list(set(freq_matches))
        
        # Extract symbols
        symbol_matches = re.findall(r"(SPX|ES|NQ|SPY|QQQ|[A-Z]{2,5})", content)
        data_req["symbols"] = list(set(symbol_matches))
        
        self.analysis["data_requirements"] = data_req
    
    def _extract_performance_targets(self, content: str) -> None:
        """Extract performance targets and expectations."""
        performance = {
            "return_targets": [],
            "win_rate_targets": [],
            "execution_speed": [],
            "scalability": []
        }
        
        # Look for performance targets
        perf_patterns = [
            r"(?i)(?:expected|target).*?return:?\s*(\d+(?:\.\d+)?)%",
            r"(?i)win.*?rate:?\s*(\d+(?:\.\d+)?)%",
            r"(?i)execution.*?time:?\s*(<?\s*\d+)\s*(seconds?|minutes?)",
            r"(?i)memory.*?usage:?\s*(<?\s*\d+)\s*(GB|MB)"
        ]
        
        for pattern in perf_patterns:
            matches = re.findall(pattern, content)
            if "return" in pattern:
                performance["return_targets"].extend([m[0] if isinstance(m, tuple) else m for m in matches])
            elif "win" in pattern:
                performance["win_rate_targets"].extend([m[0] if isinstance(m, tuple) else m for m in matches])
            elif "execution" in pattern or "time" in pattern:
                performance["execution_speed"].extend([f"{m[0]} {m[1]}" if isinstance(m, tuple) else m for m in matches])
        
        self.analysis["performance_targets"] = performance
    
    def _extract_compliance_requirements(self, content: str) -> None:
        """Extract regulatory and compliance requirements."""
        compliance = {
            "regulatory_frameworks": [],
            "risk_disclosures": [],
            "reporting_requirements": [],
            "audit_requirements": []
        }
        
        # Look for compliance mentions
        if any(term in content.lower() for term in ["regulatory", "compliance", "cftc", "sec", "finra"]):
            compliance["regulatory_frameworks"].append("US_SECURITIES")
        
        if "risk disclosure" in content.lower() or "risk warning" in content.lower():
            compliance["risk_disclosures"].append("MANDATORY_RISK_WARNINGS")
        
        self.analysis["compliance_requirements"] = compliance
    
    def _generate_test_categories(self) -> None:
        """Generate test categories based on extracted information."""
        categories = {}
        
        # Always include core categories
        categories["data_management"] = {
            "tests": 15,
            "description": "Market data retrieval, validation, and quality checks",
            "priority": "high"
        }
        
        if self.analysis["parameters"]:
            categories["strategy_parameters"] = {
                "tests": len(self.analysis["parameters"]) + 5,
                "description": "Parameter validation, relationships, and constraints",
                "priority": "high"
            }
        
        if self.analysis["trading_logic"]["entry_conditions"] or self.analysis["trading_logic"]["exit_conditions"]:
            categories["trading_logic"] = {
                "tests": 16,
                "description": "Entry/exit signals, session management, and signal generation",
                "priority": "high"
            }
        
        if self.analysis["risk_management"]["risk_controls"]:
            categories["risk_management"] = {
                "tests": 10,
                "description": "Position sizing, risk controls, and limit enforcement",
                "priority": "high"
            }
        
        # Add UI category if this appears to be a UI-based strategy
        if "streamlit" in str(self.analysis).lower() or "ui" in str(self.analysis).lower():
            categories["ui_components"] = {
                "tests": 94,
                "description": "User interface components and interactions",
                "priority": "medium"
            }
        
        # Always include these
        categories.update({
            "transaction_costs": {
                "tests": 8,
                "description": "Cost calculations and impact analysis",
                "priority": "medium"
            },
            "performance_analytics": {
                "tests": 10,
                "description": "Trade analytics and portfolio metrics",
                "priority": "medium"
            },
            "edge_cases": {
                "tests": 15,
                "description": "Error handling and market anomalies",
                "priority": "medium"
            },
            "integration": {
                "tests": 8,
                "description": "End-to-end and component integration testing",
                "priority": "high"
            },
            "performance": {
                "tests": 8,
                "description": "Execution speed and scalability testing",
                "priority": "low"
            }
        })
        
        if self.analysis["compliance_requirements"]["regulatory_frameworks"]:
            categories["regulatory_compliance"] = {
                "tests": 8,
                "description": "Trading rules and regulatory compliance",
                "priority": "medium"
            }
        
        self.analysis["test_categories"] = categories
    
    def _infer_parameter_type(self, description: str) -> str:
        """Infer parameter type from description."""
        desc_lower = description.lower()
        
        if any(term in desc_lower for term in ["$", "dollar", "capital", "amount"]):
            return "currency"
        elif any(term in desc_lower for term in ["%", "percent", "percentage"]):
            return "percentage"
        elif any(term in desc_lower for term in ["point", "pts", "pip"]):
            return "points"
        elif any(term in desc_lower for term in ["ratio", ":"]):
            return "ratio"
        elif any(term in desc_lower for term in ["time", "hour", "minute", "am", "pm"]):
            return "time"
        elif any(term in desc_lower for term in ["true", "false", "enable", "disable"]):
            return "boolean"
        elif re.search(r"\d+", description):
            return "numeric"
        else:
            return "string"


def main():
    parser = argparse.ArgumentParser(description="Analyze strategy requirements document")
    parser.add_argument("--input", required=True, help="Path to requirements document")
    parser.add_argument("--framework-name", required=True, help="Name of the test framework")
    parser.add_argument("--output", required=True, help="Output JSON file path")
    
    args = parser.parse_args()
    
    analyzer = RequirementsAnalyzer()
    analysis = analyzer.analyze_document(Path(args.input), args.framework_name)
    
    # Save analysis to JSON file
    with open(args.output, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"✅ Analysis complete. Results saved to {args.output}")
    print(f"📊 Found {len(analysis['test_categories'])} test categories")
    print(f"🎯 Strategy type: {analysis['strategy_type']}")
    print(f"⚙️  Parameters: {len(analysis['parameters'])}")


if __name__ == "__main__":
    main()