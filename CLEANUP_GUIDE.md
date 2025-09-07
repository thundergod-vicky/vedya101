# VEDYA Platform Cleanup

The following files are recommended for cleanup:

## Temporary OpenAI Testing Files
- model_access_check.js
- compare_openai_keys.js
- model_check_result.json
- model_test_report.txt
- model_test_results.json
- diagnose_openai_key.py
- comprehensive_model_test.py
- quick_model_test.py
- test_models.py
- test_openai.py
- test_openai_new.py
- test_openai_models.py

## Demo and Legacy Versions
- demo_agents.py
- demo_langgraph.py
- vedya_agents_langgraph.py
- vedya_agents_langgraph_v2.py
- simple_planning_agent.py

## Unit Tests (keep only what's needed)
- test_ai_planning.py
- test_ai_planning_dict.py
- test_clerk_flow.py
- test_conversational_chat.py
- test_email.py
- test_langgraph_quick.py
- test_planning_agent.py
- final_test.py
- terminal_chat.py (terminal test only)

## Validation Scripts (consider keeping)
- validate_langgraph.py
- verify_ses_emails.py  
- verify_supabase.py
- reset_supabase.py
- setup_langgraph.py
- setup_supabase.py

## Core files to keep:
- api_server.py
- vedya_agents.py
- ai_planning_agent.py
- ai_planning_dict.py
- conversational_agent.py
- conversational_chat.py
- professional_planning.py
- email_service.py
- user_service.py
- strict_env.py
- test_api.py (API testing)
- deploy.py

## Documentation (keep all)
- README.md
- README_AGENTS.md
- MODEL_STRATEGY.md
- DEPLOYMENT_GUIDE.md
- SES_SETUP_GUIDE.md
- CLERK_INTEGRATION_GUIDE.md
- FRONTEND_SUMMARY.md

## Configuration 
- .env (update with secure values)
- .env.example (sanitized)
- .env.langgraph (update with secure values)
- requirements.txt
- package.json
- vercel.json
- Procfile

## Recommended deletion command:
```powershell
# Run with caution - first backup important files
# This removes all test files and temporary diagnostics

foreach ($file in @(
    "model_access_check.js",
    "compare_openai_keys.js",
    "model_check_result.json",
    "model_test_report.txt",
    "model_test_results.json",
    "diagnose_openai_key.py",
    "comprehensive_model_test.py", 
    "quick_model_test.py",
    "test_models.py",
    "test_openai.py",
    "test_openai_new.py",
    "test_openai_models.py",
    "demo_agents.py",
    "demo_langgraph.py",
    "terminal_chat.py",
    "final_test.py"
)) {
    if (Test-Path $file) {
        Remove-Item -Path $file -Force
        Write-Host "Removed: $file"
    } else {
        Write-Host "Not found: $file"
    }
}
```
