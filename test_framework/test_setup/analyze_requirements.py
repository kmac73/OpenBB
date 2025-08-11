#!/usr/bin/env python3
"""
OpenBB Test Framework Generator - Interactive Requirements Analyzer
Interactively gathers testing requirements from user with no assumptions.
"""

import argparse
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys


class InteractiveRequirementsAnalyzer:
    """Interactively analyzes strategy requirements with user input and explicit assumption tracking."""
    
    def __init__(self):
        self.requirements_text = ""
        self.framework_name = ""
        self.user_inputs = {}  # Track all user-provided information
        self.documented_assumptions = {}  # Track assumptions explicitly stated by user
        self.analysis_results = {
            "framework_name": "",
            "strategy_type": "unknown",
            "user_inputs": {},
            "documented_assumptions": {},
            "test_categories": {},
            "data_requirements": {},
            "system_components": {},
            "testing_scope": {}
        }
    
    def analyze_requirements(self, input_file: Path, framework_name: str, output_file: Path):
        """Analyze requirements document first, then ask about gaps."""
        print(f"📖 Reading strategy document: {input_file}")
        
        # Read requirements document
        with open(input_file, 'r', encoding='utf-8') as f:
            self.requirements_text = f.read()
        
        self.framework_name = framework_name
        self.analysis_results["framework_name"] = framework_name
        
        print(f"\n🎯 Smart Requirements Analysis for: {framework_name}")
        print("=" * 60)
        print("First, I'll extract what I can from the requirements document.")
        print("Then I'll only ask about gaps or unclear areas.")
        print("=" * 60)
        
        # Step 1: Extract everything possible from the document
        print("\n🔍 STEP 1: Extracting information from requirements document...")
        self._extract_from_document()
        self._print_extracted_info()
        
        # Step 2: Only ask about what's missing or unclear
        print("\n❓ STEP 2: Asking about gaps and unclear areas...")
        self._ask_about_gaps()
        
        # Finalize analysis
        self.analysis_results["user_inputs"] = self.user_inputs
        self.analysis_results["documented_assumptions"] = self.documented_assumptions
        
        # Save results
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Analysis complete. Results saved to: {output_file}")
        self._print_analysis_summary()
    
    def _ask_user(self, question: str, key: str, options: Optional[List[str]] = None, 
                  required: bool = True, multiline: bool = False) -> str:
        """Ask user a question and store their response."""
        print(f"\n❓ {question}")
        
        if options:
            for i, option in enumerate(options, 1):
                print(f"   {i}. {option}")
            print(f"   {len(options) + 1}. Other (please specify)")
        
        if multiline:
            print("   (Press Enter twice to finish, or 'skip' to skip)")
            lines = []
            while True:
                line = input("   > ")
                if line.lower() == 'skip' and not required:
                    return "skipped"
                if line == "" and lines:
                    break
                lines.append(line)
            response = "\n".join(lines)
        else:
            response = input("   > ").strip()
        
        if not response and required:
            print("   ⚠️  This field is required. Please provide an answer.")
            return self._ask_user(question, key, options, required, multiline)
        
        if not response and not required:
            response = "not specified"
        
        # Handle option selection
        if options and response.isdigit():
            option_num = int(response)
            if 1 <= option_num <= len(options):
                response = options[option_num - 1]
            elif option_num == len(options) + 1:
                response = input("   Please specify: ").strip()
        
        self.user_inputs[key] = response
        return response
    
    def _ask_assumption(self, assumption_text: str, key: str) -> bool:
        """Ask user to confirm or deny an assumption."""
        print(f"\n🤔 ASSUMPTION CHECK: {assumption_text}")
        response = input("   Is this assumption correct? (y/n/explain): ").strip().lower()
        
        if response == 'y':
            self.documented_assumptions[key] = {"assumption": assumption_text, "confirmed": True, "explanation": ""}
            return True
        elif response == 'n':
            explanation = input("   Please explain what's actually the case: ").strip()
            self.documented_assumptions[key] = {"assumption": assumption_text, "confirmed": False, "explanation": explanation}
            return False
        elif response == 'explain':
            explanation = input("   Please provide clarification: ").strip()
            confirmed = input("   After clarification, is the assumption correct? (y/n): ").strip().lower() == 'y'
            self.documented_assumptions[key] = {"assumption": assumption_text, "confirmed": confirmed, "explanation": explanation}
            return confirmed
        else:
            print("   Please answer 'y', 'n', or 'explain'")
            return self._ask_assumption(assumption_text, key)
    
    def _interactive_strategy_overview(self):
        """Get high-level strategy information from user."""
        print("\n📋 SECTION 1: Strategy Overview")
        print("-" * 30)
        
        strategy_type = self._ask_user(
            "What type of trading strategy is this?",
            "strategy_type",
            ["Live Trading Strategy", "Backtesting/Analysis Strategy", "Simulation Strategy", "Hybrid (Live + Backtest)"]
        )
        
        self.analysis_results["strategy_type"] = strategy_type.lower().replace(" ", "_")
        
        self._ask_user(
            "Briefly describe what this strategy does:",
            "strategy_description",
            multiline=True
        )
        
        self._ask_user(
            "What markets/instruments does this strategy trade?",
            "target_instruments",
            multiline=True
        )
    
    def _interactive_data_requirements(self):
        """Understand data requirements with no assumptions."""
        print("\n📊 SECTION 2: Data Requirements")
        print("-" * 30)
        
        needs_data = self._ask_user(
            "Does this strategy require any data input (historical prices, real-time feeds, etc.)?",
            "needs_data",
            ["Yes", "No"]
        )
        
        if needs_data.lower() == "yes":
            data_types = self._ask_user(
                "What types of data does it need?",
                "data_types",
                ["Historical price data", "Real-time price feeds", "Fundamental data", 
                 "Alternative data", "Broker-specific data", "Custom data files"],
                multiline=True
            )
            
            data_sources = self._ask_user(
                "What are the specific data sources (e.g., yfinance, broker API, files, etc.)?",
                "data_sources",
                multiline=True
            )
            
            data_frequencies = self._ask_user(
                "What data frequencies are needed (e.g., 1min, 5min, daily, real-time)?",
                "data_frequencies",
                multiline=True
            )
            
            self.analysis_results["data_requirements"] = {
                "needs_data": True,
                "data_types": data_types,
                "data_sources": data_sources,
                "data_frequencies": data_frequencies
            }
        else:
            self.analysis_results["data_requirements"] = {"needs_data": False}
    
    def _interactive_system_components(self):
        """Identify system components to test."""
        print("\n🔧 SECTION 3: System Components")
        print("-" * 30)
        
        components = []
        
        # Ask about each potential component type
        component_types = [
            ("Data retrieval/management", "data_management"),
            ("Trading logic/algorithms", "trading_logic"),
            ("Risk management systems", "risk_management"),
            ("User interface (web app, dashboard)", "user_interface"),
            ("Database/storage systems", "database"),
            ("External API integrations", "api_integrations"),
            ("Configuration/parameter management", "configuration"),
            ("Reporting/analytics", "reporting"),
            ("Order execution systems", "order_execution"),
            ("Performance monitoring", "performance_monitoring")
        ]
        
        for component_name, component_key in component_types:
            has_component = self._ask_user(
                f"Does your strategy include {component_name}?",
                f"has_{component_key}",
                ["Yes", "No", "Not sure"]
            )
            
            if has_component.lower() == "yes":
                details = self._ask_user(
                    f"Please describe the {component_name} component:",
                    f"{component_key}_details",
                    multiline=True,
                    required=False
                )
                components.append({"name": component_name, "key": component_key, "details": details})
        
        self.analysis_results["system_components"] = components
    
    def _interactive_testing_scope(self):
        """Define testing scope and priorities."""
        print("\n🎯 SECTION 4: Testing Scope")
        print("-" * 30)
        
        testing_goals = self._ask_user(
            "What are your main testing goals?",
            "testing_goals",
            ["Verify correctness", "Performance testing", "Error handling", 
             "Integration testing", "Regression testing", "All of the above"],
            multiline=True
        )
        
        priority_areas = self._ask_user(
            "Which areas are highest priority for testing?",
            "priority_areas",
            multiline=True
        )
        
        edge_cases = self._ask_user(
            "Are there specific edge cases or error conditions you're concerned about?",
            "edge_cases",
            multiline=True,
            required=False
        )
        
        self.analysis_results["testing_scope"] = {
            "testing_goals": testing_goals,
            "priority_areas": priority_areas,
            "edge_cases": edge_cases
        }
    
    def _extract_from_document(self):
        """Extract as much information as possible from the requirements document."""
        doc_lower = self.requirements_text.lower()
        
        # Extract strategy type
        self._extract_strategy_type()
        
        # Extract strategy description
        self._extract_strategy_description()
        
        # Extract instruments/markets
        self._extract_target_instruments()
        
        # Extract data requirements
        self._extract_data_requirements_from_doc()
        
        # Extract system components mentioned in document
        self._extract_system_components_from_doc()
        
        # Extract testing-related information
        self._extract_testing_info_from_doc()
    
    def _extract_strategy_type(self):
        """Extract strategy type from document content."""
        doc_lower = self.requirements_text.lower()
        
        # Look for explicit strategy type indicators
        if any(term in doc_lower for term in ['cfd', 'contract for difference']):
            strategy_type = "Live Trading Strategy (CFD)"
        elif any(term in doc_lower for term in ['backtest', 'historical', 'simulation']):
            strategy_type = "Backtesting/Analysis Strategy"
        elif any(term in doc_lower for term in ['real-time', 'live trading', 'broker']):
            strategy_type = "Live Trading Strategy"
        else:
            strategy_type = "Not clearly specified"
        
        self.analysis_results["strategy_type"] = strategy_type
        self.user_inputs["strategy_type_extracted"] = strategy_type
    
    def _extract_strategy_description(self):
        """Extract strategy description from document."""
        # Look for executive summary or overview sections
        patterns = [
            r"(?i)##?\s*executive\s+summary\s*(.*?)(?=\n##|\n#|$)",
            r"(?i)##?\s*overview\s*(.*?)(?=\n##|\n#|$)",
            r"(?i)##?\s*strategy\s+overview\s*(.*?)(?=\n##|\n#|$)"
        ]
        
        description = ""
        for pattern in patterns:
            matches = re.findall(pattern, self.requirements_text, re.DOTALL)
            if matches:
                description = matches[0].strip()[:500]  # First 500 chars
                break
        
        if not description:
            # Take first paragraph as fallback
            paragraphs = self.requirements_text.split('\n\n')
            for para in paragraphs:
                if len(para.strip()) > 50:  # Substantial paragraph
                    description = para.strip()[:500]
                    break
        
        self.analysis_results["strategy_description"] = description
        self.user_inputs["strategy_description_extracted"] = description
    
    def _extract_target_instruments(self):
        """Extract target instruments/markets from document."""
        instruments = []
        
        # Look for common instrument mentions
        instrument_patterns = [
            r"S&P\s*500", r"SPX", r"ES", r"SPY",
            r"CFD", r"contract for difference",
            r"futures", r"options", r"forex", r"crypto"
        ]
        
        for pattern in instrument_patterns:
            if re.search(pattern, self.requirements_text, re.IGNORECASE):
                instruments.append(pattern.replace(r"\s*", " ").replace(r"\s+", " "))
        
        instruments_text = ", ".join(set(instruments)) if instruments else "Not explicitly specified"
        self.analysis_results["target_instruments"] = instruments_text
        self.user_inputs["target_instruments_extracted"] = instruments_text
    
    def _extract_data_requirements_from_doc(self):
        """Extract data requirements from document."""
        doc_lower = self.requirements_text.lower()
        
        # Check if strategy needs data
        data_indicators = [
            'real-time', 'historical', 'price data', 'market data', 
            'broker feed', 'data source', 'pricing', 'ohlc'
        ]
        
        needs_data = any(term in doc_lower for term in data_indicators)
        
        data_req = {"needs_data": needs_data}
        
        if needs_data:
            # Extract data types
            data_types = []
            if any(term in doc_lower for term in ['real-time', 'live', 'streaming']):
                data_types.append("Real-time price feeds")
            if any(term in doc_lower for term in ['historical', 'backtest', 'past']):
                data_types.append("Historical price data")
            if any(term in doc_lower for term in ['broker', 'platform']):
                data_types.append("Broker-specific data")
            
            # Extract data sources (look for specific mentions)
            data_sources = []
            source_patterns = [
                r"yfinance", r"yahoo\s+finance", r"bloomberg", r"reuters",
                r"broker\s+(?:api|feed)", r"trading\s+platform"
            ]
            
            for pattern in source_patterns:
                if re.search(pattern, self.requirements_text, re.IGNORECASE):
                    data_sources.append(pattern.replace(r"\s+", " "))
            
            # Extract frequencies
            frequencies = []
            freq_patterns = [
                r"\d+[mM](?:in)?", r"\d+[hH](?:our)?", r"daily", r"1D",
                r"intraday", r"real[- ]?time"
            ]
            
            for pattern in freq_patterns:
                matches = re.findall(pattern, self.requirements_text)
                frequencies.extend(matches)
            
            data_req.update({
                "data_types": ", ".join(set(data_types)) if data_types else "Not specified",
                "data_sources": ", ".join(set(data_sources)) if data_sources else "Not specified", 
                "data_frequencies": ", ".join(set(frequencies)) if frequencies else "Not specified"
            })
        
        self.analysis_results["data_requirements"] = data_req
    
    def _extract_system_components_from_doc(self):
        """Extract system components mentioned in document."""
        doc_lower = self.requirements_text.lower()
        components = []
        
        # Component detection patterns
        component_checks = [
            ("Trading logic/algorithms", ["entry", "exit", "signal", "algorithm", "logic", "strategy"]),
            ("Risk management systems", ["risk", "stop loss", "position size", "drawdown", "leverage"]),
            ("Order execution systems", ["order", "execution", "broker", "trade", "position"]),
            ("Performance monitoring", ["performance", "monitoring", "analytics", "metrics", "reporting"]),
            ("Configuration/parameter management", ["parameter", "config", "setting", "threshold"]),
            ("User interface", ["ui", "interface", "dashboard", "streamlit", "web"]),
            ("Database/storage systems", ["database", "storage", "persistence", "data store"]),
            ("External API integrations", ["api", "integration", "external", "third party"])
        ]
        
        for component_name, keywords in component_checks:
            if any(keyword in doc_lower for keyword in keywords):
                # Extract some context about this component
                details = f"Mentioned in requirements document with keywords: {', '.join([k for k in keywords if k in doc_lower])}"
                components.append({
                    "name": component_name,
                    "key": component_name.lower().replace(" ", "_").replace("/", "_"),
                    "details": details,
                    "extracted_from_doc": True
                })
        
        self.analysis_results["system_components"] = components
    
    def _extract_testing_info_from_doc(self):
        """Extract any testing-related information from document."""
        doc_lower = self.requirements_text.lower()
        
        # Look for testing, validation, or verification mentions
        testing_keywords = [
            "test", "validation", "verification", "robustness", "backtesting",
            "simulation", "monte carlo", "walk-forward", "out-of-sample"
        ]
        
        testing_mentions = [kw for kw in testing_keywords if kw in doc_lower]
        
        if testing_mentions:
            self.analysis_results["testing_scope"] = {
                "testing_goals": f"Document mentions: {', '.join(testing_mentions)}",
                "priority_areas": "Based on document analysis",
                "edge_cases": "To be determined based on document content"
            }
    
    def _print_extracted_info(self):
        """Print what was extracted from the document."""
        print(f"✅ Strategy Type: {self.analysis_results['strategy_type']}")
        print(f"✅ Target Instruments: {self.analysis_results.get('target_instruments', 'Not found')}")
        
        data_req = self.analysis_results.get("data_requirements", {})
        print(f"✅ Needs Data: {data_req.get('needs_data', 'Unknown')}")
        if data_req.get("needs_data"):
            print(f"   - Data Types: {data_req.get('data_types', 'Not specified')}")
            print(f"   - Data Sources: {data_req.get('data_sources', 'Not specified')}")
            print(f"   - Frequencies: {data_req.get('data_frequencies', 'Not specified')}")
        
        components = self.analysis_results.get("system_components", [])
        print(f"✅ System Components Found: {len(components)}")
        for comp in components:
            print(f"   - {comp['name']}")
    
    def _ask_about_gaps(self):
        """Only ask about information that couldn't be extracted from document."""
        print("Now I'll ask about anything that wasn't clear from the document...\n")
        
        # Only ask about data requirements if they weren't clear
        data_req = self.analysis_results.get("data_requirements", {})
        if not data_req.get("needs_data") or data_req.get("data_sources") == "Not specified":
            self._ask_about_missing_data_info()
        
        # Ask about testing priorities (this is usually not in requirements docs)
        self._ask_about_testing_priorities()
        
        # Ask about test categories based on what was found
        self._generate_test_categories_from_extracted_info()
    
    def _ask_about_missing_data_info(self):
        """Ask about data requirements that couldn't be determined from document."""
        data_req = self.analysis_results.get("data_requirements", {})
        
        if data_req.get("data_sources") == "Not specified":
            data_sources = self._ask_user(
                "The document doesn't specify exact data sources. What data sources will this strategy use?",
                "clarified_data_sources",
                ["Broker API/feeds", "File-based data", "Third-party data provider", "Multiple sources"],
                multiline=True
            )
            data_req["data_sources"] = data_sources
        
        if data_req.get("data_frequencies") == "Not specified":
            frequencies = self._ask_user(
                "What data frequencies does this strategy need?",
                "clarified_frequencies", 
                ["Real-time (streaming)", "1-minute bars", "5-minute bars", "Daily bars", "Multiple frequencies"],
                multiline=True
            )
            data_req["data_frequencies"] = frequencies
    
    def _ask_about_testing_priorities(self):
        """Ask about testing priorities and goals."""
        testing_goals = self._ask_user(
            "What are your main testing goals for this strategy?",
            "testing_goals",
            ["Verify correctness", "Performance testing", "Error handling", 
             "Integration testing", "Regression testing", "All of the above"]
        )
        
        priority_areas = self._ask_user(
            "Which areas are highest priority for testing?",
            "priority_areas",
            multiline=True
        )
        
        self.analysis_results["testing_scope"] = {
            "testing_goals": testing_goals,
            "priority_areas": priority_areas,
            "edge_cases": "Standard edge cases plus strategy-specific scenarios"
        }
    
    def _generate_test_categories_from_extracted_info(self):
        """Generate test categories based on extracted components."""
        categories = {}
        
        # Generate categories for each component found in document  
        for component in self.analysis_results.get("system_components", []):
            component_key = component["key"]
            component_name = component["name"]
            
            # Estimate test count based on component type
            test_estimates = {
                "trading_logic_algorithms": 15,
                "risk_management_systems": 12,
                "order_execution_systems": 18,
                "performance_monitoring": 10,
                "configuration_parameter_management": 8,
                "user_interface": 15,
                "database_storage_systems": 10,
                "external_api_integrations": 12
            }
            
            estimated_tests = test_estimates.get(component_key, 8)
            
            wants_tests = self._ask_user(
                f"Generate comprehensive tests for {component_name}? (Found in document)",
                f"test_{component_key}",
                ["Yes - High Priority", "Yes - Medium Priority", "Yes - Low Priority", "Skip"]
            )
            
            if "yes" in wants_tests.lower():
                priority = "high" if "high" in wants_tests.lower() else \
                          "medium" if "medium" in wants_tests.lower() else "low"
                
                categories[component_key] = {
                    "tests": estimated_tests,
                    "priority": priority,
                    "description": component["details"]
                }
        
        self.analysis_results["test_categories"] = categories
    
    def _interactive_test_categories(self):
        """Build test categories based on user input."""
        print("\n🧪 SECTION 5: Test Categories")
        print("-" * 30)
        
        categories = {}
        
        # Generate categories based on identified components
        for component in self.analysis_results["system_components"]:
            component_key = component["key"]
            component_name = component["name"]
            
            wants_tests = self._ask_user(
                f"Do you want comprehensive tests for {component_name}?",
                f"test_{component_key}",
                ["Yes - High Priority", "Yes - Medium Priority", "Yes - Low Priority", "No"]
            )
            
            if "yes" in wants_tests.lower():
                priority = "high" if "high" in wants_tests.lower() else \
                          "medium" if "medium" in wants_tests.lower() else "low"
                
                estimated_tests = self._ask_user(
                    f"How many test scenarios would you estimate for {component_name}? (rough number)",
                    f"test_count_{component_key}",
                    required=False
                )
                
                try:
                    test_count = int(estimated_tests) if estimated_tests.isdigit() else 5
                except:
                    test_count = 5
                
                categories[component_key] = {
                    "tests": test_count,
                    "priority": priority,
                    "description": component["details"][:100] + "..." if len(component["details"]) > 100 else component["details"]
                }
        
        # Ask about additional categories
        additional_categories = self._ask_user(
            "Are there any other testing areas not covered above?",
            "additional_categories",
            multiline=True,
            required=False
        )
        
        if additional_categories and additional_categories != "not specified":
            categories["custom_additional"] = {
                "tests": 5,
                "priority": "medium",
                "description": additional_categories
            }
        
        self.analysis_results["test_categories"] = categories
    
    def _print_analysis_summary(self):
        """Print comprehensive summary of analysis."""
        print("\n" + "=" * 60)
        print("📊 ANALYSIS SUMMARY")
        print("=" * 60)
        
        print(f"Framework Name: {self.analysis_results['framework_name']}")
        print(f"Strategy Type: {self.analysis_results['strategy_type']}")
        
        print(f"\n📋 User Inputs Collected: {len(self.user_inputs)}")
        for key, value in self.user_inputs.items():
            if isinstance(value, str) and len(value) > 100:
                print(f"  {key}: {value[:100]}...")
            else:
                print(f"  {key}: {value}")
        
        print(f"\n🤔 Documented Assumptions: {len(self.documented_assumptions)}")
        for key, assumption in self.documented_assumptions.items():
            status = "✅ CONFIRMED" if assumption["confirmed"] else "❌ REJECTED"
            print(f"  {key}: {status}")
            print(f"    Assumption: {assumption['assumption']}")
            if assumption["explanation"]:
                print(f"    Explanation: {assumption['explanation']}")
        
        print(f"\n🧪 Test Categories to Generate: {len(self.analysis_results['test_categories'])}")
        total_tests = 0
        for category, info in self.analysis_results['test_categories'].items():
            print(f"  {category}: {info['tests']} tests ({info['priority']} priority)")
            total_tests += info['tests']
        
        print(f"\n📈 Total Estimated Tests: {total_tests}")
        
        print(f"\n💾 All information saved to analysis file for test generation.")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Interactive strategy requirements analysis")
    parser.add_argument("--input", required=True, help="Path to requirements document")
    parser.add_argument("--framework-name", required=True, help="Name of the test framework")
    parser.add_argument("--output", required=True, help="Path to output JSON file")
    
    args = parser.parse_args()
    
    analyzer = InteractiveRequirementsAnalyzer()
    analyzer.analyze_requirements(Path(args.input), args.framework_name, Path(args.output))


if __name__ == "__main__":
    main()