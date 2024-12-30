#!/bin/bash
# Install Python dependencies
pip install -r requirements.txt

# Run the Streamlit server
streamlit run main_with_audio.py --server.port 8501 --server.address 0.0.0.0
