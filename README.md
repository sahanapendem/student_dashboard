# 1. Project Directory Real Estate

engineering_app/
│
├── .secrets/
│   └── secrets.toml          # Secure Local Environment (Ignored by Git)
├── analytics_dashboard/
│   └── app.py                # Core Python Program Source File
├── .gitignore                # Protects connection files from leaks
├── requirements.txt          # Global Application Library Dependencies
└── README.md                 # Project Blueprint documentation
# 2. Prepare System Requirements
Open your project directory within your command prompt terminal and run the environmental compiler command:

# Bash
pip install -r requirements.txt

python -m streamlit run analytics_dashboard/app.py
