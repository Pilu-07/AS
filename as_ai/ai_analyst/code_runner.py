import sys
import io
import contextlib
import base64
import os
import uuid
from typing import Dict, Any

def execute_analysis_code(code: str, df) -> Dict[str, Any]:
    """
    Executes Python code in a restricted namespace with access to the dataset `df`.
    Captures stdout and any generated matplotlib plots.
    """
    # Create an isolated environment matching allowed libraries
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    import sklearn
    
    # Custom savefig to capture charts without writing to disk
    charts = []
    
    def mock_savefig(*args, **kwargs):
        from io import BytesIO
        buf = BytesIO()
        plt.gcf().savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        
        # We save it to a /charts/ file to serve to frontend dynamically
        charts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend_public", "charts")
        os.makedirs(charts_dir, exist_ok=True)
        filename = f"analyst_{uuid.uuid4().hex}.png"
        
        with open(os.path.join(charts_dir, filename), "wb") as f:
            f.write(base64.b64decode(img_str))
            
        charts.append(f"/charts/{filename}")
        
    plt.savefig = mock_savefig
    
    namespace = {
        'df': df.copy(),
        'pd': pd,
        'np': np,
        'plt': plt,
        'sns': sns,
        'sklearn': sklearn,
        'result_data': {} # dictionary for the code to dump specific structured results
    }
    
    output_buffer = io.StringIO()
    error = None
    
    try:
        with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
            exec(code, namespace)
    except Exception as e:
        import traceback
        error = traceback.format_exc()

    plt.close('all') # Cleanup any open figures

    return {
        "output": output_buffer.getvalue(),
        "error": error,
        "charts": charts,
        "result_data": namespace.get("result_data", {})
    }
