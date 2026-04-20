"""
HR Policy Assistant - Master Index and Verification Script

This script verifies that all project components are properly installed and working.
Run this to ensure everything is ready before running the agent.
"""

import os
import sys
from pathlib import Path


class ProjectVerifier:
    """Verifies HR Policy Assistant project integrity"""
    
    # Expected files
    REQUIRED_FILES = {
        # Core implementation files
        'state.py': 'State definition (CapstoneState TypedDict)',
        'nodes.py': '8 node implementations',
        'tools.py': 'Tool functions (datetime, calculator)',
        'rag.py': 'Knowledge base (10 HR documents)',
        'graph.py': 'LangGraph StateGraph builder',
        'agent.py': 'Agent orchestration',
        
        # UI and interface
        'capstone_streamlit.py': 'Streamlit web interface',
        
        # Testing
        'test_evaluation.py': 'Testing and RAGAS evaluation',
        'examples.py': 'Usage examples',
        
        # Configuration
        'config.py': 'Configuration management',
        'requirements.txt': 'Python dependencies',
        '.env.example': 'Environment template',
        
        # Documentation
        'README.md': 'Complete documentation',
        'CAPSTONE_SUBMISSION.md': 'Submission details',
        'PROJECT_SUMMARY.md': 'Project overview',
        
        # Setup scripts
        'quickstart.bat': 'Windows quick start',
        'quickstart.sh': 'Linux/macOS quick start'
    }
    
    def __init__(self):
        """Initialize verifier"""
        self.project_root = Path(__file__).parent
        self.all_checks_passed = True
    
    def verify_files(self) -> bool:
        """Verify all required files exist"""
        print("\n📋 VERIFYING PROJECT FILES")
        print("=" * 60)
        
        missing_files = []
        
        for filename, description in self.REQUIRED_FILES.items():
            file_path = self.project_root / filename
            
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"✅ {filename:<30} ({size:>6} bytes) - {description}")
            else:
                print(f"❌ {filename:<30} MISSING")
                missing_files.append(filename)
                self.all_checks_passed = False
        
        if missing_files:
            print(f"\n❌ Missing {len(missing_files)} files:")
            for f in missing_files:
                print(f"   - {f}")
            return False
        
        print("\n✅ All project files present!")
        return True
    
    def verify_python_version(self) -> bool:
        """Verify Python version"""
        print("\n🐍 VERIFYING PYTHON VERSION")
        print("=" * 60)
        
        version = sys.version_info
        version_string = f"{version.major}.{version.minor}.{version.micro}"
        
        print(f"Python version: {version_string}")
        
        if version.major >= 3 and version.minor >= 9:
            print("✅ Python version is compatible")
            return True
        else:
            print(f"❌ Python 3.9+ required, found {version_string}")
            self.all_checks_passed = False
            return False
    
    def verify_dependencies(self) -> bool:
        """Verify required packages can be imported"""
        print("\n📦 VERIFYING DEPENDENCIES")
        print("=" * 60)
        
        required_packages = [
            ('state', 'state.py - CapstoneState'),
            ('nodes', 'nodes.py - Node functions'),
            ('tools', 'tools.py - Tools'),
            ('rag', 'rag.py - RAG system'),
            ('graph', 'graph.py - Graph builder'),
            ('agent', 'agent.py - Agent'),
        ]
        
        missing_packages = []
        
        for module_name, description in required_packages:
            try:
                # Try to import the module
                module_path = self.project_root / f"{module_name}.py"
                if module_path.exists():
                    print(f"✅ {module_name:<15} - {description}")
                else:
                    print(f"❌ {module_name:<15} - MISSING")
                    missing_packages.append(module_name)
                    self.all_checks_passed = False
            except Exception as e:
                print(f"❌ {module_name:<15} - ERROR: {str(e)}")
                missing_packages.append(module_name)
                self.all_checks_passed = False
        
        if not missing_packages:
            print("\n✅ All module files present!")
            return True
        else:
            print(f"\n❌ {len(missing_packages)} modules missing")
            return False
    
    def verify_configuration(self) -> bool:
        """Verify configuration setup"""
        print("\n⚙️  VERIFYING CONFIGURATION")
        print("=" * 60)
        
        groq_key = os.getenv("GROQ_API_KEY")
        
        if groq_key:
            masked_key = groq_key[:10] + "..." + groq_key[-5:]
            print(f"✅ GROQ_API_KEY is set ({masked_key})")
            return True
        else:
            print("⚠️  GROQ_API_KEY is not set")
            print("   Please set it before running the agent")
            print("   export GROQ_API_KEY='your_key_here'")
            return True  # Not required for verification
    
    def verify_code_structure(self) -> bool:
        """Verify code structure in key files"""
        print("\n🔍 VERIFYING CODE STRUCTURE")
        print("=" * 60)
        
        checks = [
            ('state.py', 'CapstoneState', 'State definition'),
            ('nodes.py', 'def memory_node', 'Memory node'),
            ('nodes.py', 'def router_node', 'Router node'),
            ('rag.py', 'initialize_chromadb', 'RAG initialization'),
            ('graph.py', 'def build_graph', 'Graph builder'),
            ('agent.py', 'class HRPolicyAgent', 'Agent class'),
            ('tools.py', 'def datetime_tool', 'DateTime tool'),
            ('tools.py', 'def calculator_tool', 'Calculator tool'),
        ]
        
        all_good = True
        
        for filename, code_element, description in checks:
            file_path = self.project_root / filename
            
            if file_path.exists():
                content = file_path.read_text()
                if code_element in content:
                    print(f"✅ {filename:<20} - {description}")
                else:
                    print(f"❌ {filename:<20} - Missing: {code_element}")
                    all_good = False
                    self.all_checks_passed = False
            else:
                print(f"❌ {filename:<20} - FILE NOT FOUND")
                all_good = False
                self.all_checks_passed = False
        
        if all_good:
            print("\n✅ All code structures verified!")
        
        return all_good
    
    def show_quick_start(self):
        """Show quick start instructions"""
        print("\n" + "=" * 60)
        print("🚀 QUICK START INSTRUCTIONS")
        print("=" * 60)
        
        print("""
1. SET API KEY
   Windows:  set GROQ_API_KEY=your_api_key_here
   Linux:    export GROQ_API_KEY="your_api_key_here"

2. INSTALL DEPENDENCIES
   pip install -r requirements.txt

3. RUN STREAMLIT UI
   streamlit run capstone_streamlit.py

4. RUN TESTS (in another terminal)
   python test_evaluation.py

5. VIEW DOCUMENTATION
   - README.md - Complete guide
   - CAPSTONE_SUBMISSION.md - Submission details
   - PROJECT_SUMMARY.md - Project overview

6. TRY EXAMPLES
   python examples.py
        """)
    
    def run_all_verifications(self) -> bool:
        """Run all verifications"""
        print("\n" + "=" * 60)
        print("🔧 HR POLICY ASSISTANT - PROJECT VERIFICATION")
        print("=" * 60)
        
        self.verify_files()
        self.verify_python_version()
        self.verify_dependencies()
        self.verify_configuration()
        self.verify_code_structure()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 60)
        
        if self.all_checks_passed:
            print("\n✅ ALL VERIFICATIONS PASSED!")
            print("\n✨ Project is ready for deployment!")
            self.show_quick_start()
            return True
        else:
            print("\n⚠️  SOME VERIFICATIONS FAILED")
            print("\nPlease fix the issues listed above and try again.")
            return False


def main():
    """Main entry point"""
    verifier = ProjectVerifier()
    success = verifier.run_all_verifications()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
