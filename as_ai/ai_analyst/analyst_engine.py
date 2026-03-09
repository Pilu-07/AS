import re
from as_ai.llm_pipeline import generate_text
from as_ai.ai_analyst.code_runner import execute_analysis_code

def analyze_dataset_query(df, question: str):
    """
    Uses the LLM to generate an analysis plan and Python code based on the user's question.
    Executes the code safely and processes the results.
    """
    
    columns = list(df.columns)
    types = [str(x) for x in df.dtypes]
    schema_str = ", ".join([f"{col} ({typ})" for col, typ in zip(columns, types)])
    row_count = len(df)
    
    prompt = f"""You are an expert AI Data Scientist.
A user asked the following question about a dataset: "{question}"

Dataset Description: {row_count} rows.
Columns: {schema_str}

Write Python code to answer this question. 
You have access to a pandas DataFrame called `df`.
You can use `pd`, `np`, `plt`, `sns`, and `sklearn`.
If you create a plot, call `plt.savefig('any_name.png')` (the backend will automatically intercept and save it properly).
Store any requested scalar answers, lists, or small summaries inside a dictionary called `result_data` which is already defined in the namespace. Do not redefine `result_data = dict()`, just set keys like `result_data['summary'] = '...'`.
Print out any reasoning needed to stdout.

Provide your analysis code inside a ```python ``` code block.
Before the code block, briefly outline your analysis plan.
"""

    llm_response = generate_text(prompt)
    
    # Extract code
    code_match = re.search(r"```python(.*?)```", llm_response, re.DOTALL)
    if not code_match:
        return {
            "analysis_summary": llm_response,
            "error": "Could not extract executable python code from the AI response."
        }
        
    code = code_match.group(1).strip()
    
    # Run code
    execution_result = execute_analysis_code(code, df)
    
    # Summarize logic based on results
    summary_prompt = f"""You just ran an analysis for the user question: "{question}"

Your code output was:
{execution_result['output']}

Extracted data:
{execution_result['result_data']}

Errors (if any):
{execution_result['error']}

Provide a highly concise, professional business-friendly summary of the answer based on these results.
Do not mention python code or execution. Just present the insight.
"""
    final_summary = generate_text(summary_prompt)

    return {
        "analysis_summary": final_summary,
        "generated_code": code,
        "detailed_output": execution_result["output"],
        "chart_data": execution_result["charts"],
        "extracted_data": execution_result["result_data"],
        "error": execution_result.get("error")
    }
